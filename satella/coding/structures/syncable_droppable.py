import bisect
import itertools
import math
from abc import ABCMeta, abstractmethod
import typing as tp

from satella.coding.concurrent.monitor import RMonitor
from satella.coding.recast_exceptions import silence_excs
from satella.coding.sequences import try_close
from satella.coding.typing import V, K, KVTuple


class DBStorage(metaclass=ABCMeta):
    """
    An abstract implementation of the storage class provided to
    :class:`~satella.coding.structures.SyncableDroppable`

    This serves as satella's hook into your database infrastructure.
    """
    __slots__ = ()

    @abstractmethod
    def put(self, key: K, value: V) -> None:
        """
        Put given value to storage at given key.

        This may block for a while.

        :param key: key to store
        :param value: value to store
        """

    @abstractmethod
    def iterate(self, starting_key: tp.Optional[K]) -> tp.Iterator[KVTuple]:
        """
        Return an iterator iterating from provided starting key to the end
        of the values, as read from the database.

        This may block for a while.

        This iterator will be closed upon no longer being necessary.

        :param starting_key: starting key, included, or None for iterate from the start
        :return: an iterator from provided key (included) to the end of the range
        """

    @abstractmethod
    def on_change_start_entry(self, start_entry: tp.Optional[K]) -> None:
        """
        Called by SyncableDroppable when starting entry (earliest entry encountered both in the DB
        and is memory) is changed.

        :param start_entry: new value of start entry or None if there are no entries at all
        """

    @abstractmethod
    def on_change_stop_entry(self, stop_entry: tp.Optional[K]) -> None:
        """
        Called by SyncableDroppable when stopping entry (earliest entry encountered both in the DB
        and is memory) is changed.

        :param stop_entry: new value of stop entry or None if there are no entries at all
        """

    @abstractmethod
    def on_change_synced_up_to(self, synced_up_to: tp.Optional[K]) -> None:
        """
        Called by SyncableDroppable when synced up to (earliest timestamp synced) is changed.

        :param synced_up_to: new value of synced up to
        """

    @abstractmethod
    def delete(self, key: K) -> None:
        """
        Called by SyncableDroppable when there's a need to remove target key

        :param key: key to remove
        """


class SyncableDroppable(RMonitor, tp.Generic[K, V]):
    """
    A thread-safe class representing some single time series, which needs to be synchronized with some server,
    and may be too large to keep in memory. Moreover, after the sync we need to retain a part of the
    time series in memory for future requests. Only series past some timestamp may be deleted.

    For brevity, this will refer to keys as timestamps. The keys must be __eq__able, comparable
    and subtractable.

    A rule is that an item can never be both in memory and in the DB.

    :param db_storage: a DBStorage implementation of your own provision, that serves as class'
        interface with the database
    :param start_entry: earliest timestamp stored or None if no data is stored
    :param stop_entry: latest timestamp stored or None if no data is stored
    :param synced_up_to: timestamp of the last entry synchronized or None if no data is stored
    :param span_to_keep_in_memory: key span to keep in memory. Entries earlier than
        difference of the latest key and this will be dropped from memory, onto the DB.
        Can't be false.
    :param span_to_keep_in_db: key span to keep on disk. Entries earlier than
        difference of the latest key and this will be dropped from the DB.
        Can't be false.

    .. note:: Note that proper handling of maximum spans requires periodical calls to
              :meth:`~satella.coding.structures.SyncableDroppable.cleanup`
    """
    __slots__ = ('db_storage', '_start_entry', '_stop_entry', '_synced_up_to', 'data_in_memory',
                 'span_to_keep_in_memory', 'span_to_keep_in_db')

    def __init__(self, db_storage: DBStorage, start_entry: tp.Optional[K],
                 stop_entry: tp.Optional[K], synced_up_to: tp.Optional[K],
                 span_to_keep_in_memory: int, span_to_keep_in_db: int):
        super().__init__()
        assert span_to_keep_in_memory and span_to_keep_in_db, 'One of spans was false!'
        assert span_to_keep_in_db > span_to_keep_in_memory, 'Invalid span'
        self.db_storage = db_storage  # type: DBStorage
        self._start_entry = start_entry  # type: K
        self._stop_entry = stop_entry  # type: K
        self._synced_up_to = synced_up_to  # type: K
        self.data_in_memory = []  # type: tp.List[KVTuple]
        self.span_to_keep_in_db = span_to_keep_in_db  # type: K
        self.span_to_keep_in_memory = span_to_keep_in_memory  # type: K

    @property
    def start_entry(self) -> tp.Optional[K]:
        return self._start_entry

    @start_entry.setter
    def start_entry(self, v: tp.Optional[K]) -> None:
        self._start_entry = v
        self.db_storage.on_change_start_entry(v)

    @property
    def synced_up_to(self) -> tp.Optional[K]:
        return self._synced_up_to

    @synced_up_to.setter
    def synced_up_to(self, v: tp.Optional[K]) -> None:
        self._synced_up_to = v
        self.db_storage.on_change_synced_up_to(v)

    @property
    def stop_entry(self) -> tp.Optional[K]:
        return self._stop_entry

    @stop_entry.setter
    def stop_entry(self, v: tp.Optional[K]) -> None:
        self._stop_entry = v
        self.db_storage.on_change_stop_entry(v)

    @RMonitor.synchronized
    def sync_to_db(self) -> None:
        """
        Make sure that everything's that in memory in also stored in the DB.
        """
        for key, value in self.data_in_memory:
            self.db_storage.put(key, value)
        self.data_in_memory = []

    def cleanup(self) -> None:
        """
        Make sure that everything's that in memory and the DB conforms to span_to_keep_in_db
        and span_to_keep_in_memory.

        This may block for a while.
        """
        self.cleanup_keep_in_db()
        self.cleanup_keep_in_memory()

    def _cleanup_the_db(self) -> bool:
        """
        Remove entries from the DB that are older than span_to_keep_in_db

        :return: if all entries in the DB have been trashed
        """
        if self.start_entry is None:
            return False
        cutoff_span = self.stop_entry - self.span_to_keep_in_db
        iterator = self.db_storage.iterate(self.start_entry)
        try:
            for key, value in iterator:
                if key < cutoff_span:
                    self.db_storage.delete(key)
                else:
                    self.start_entry = key
                    break
            else:
                # This means that we have wiped entire DB
                if self.data_in_memory:
                    self.start_entry = self.data_in_memory[0][0]
                    self.db_storage.on_change_start_entry(self.start_entry)
                else:
                    # We no longer have ANY data
                    self.start_entry = self.stop_entry = None
                return True
        finally:
            try_close(iterator)
        return False

    def get_archive(self, start: K, stop: K) -> tp.Iterator[KVTuple]:
        """
        Get some historic data that is kept both in the DB and in the memory

        :param start: starting key (included)
        :param stop: stopping key (included)
        :return: a iterator of KVTuple
        """
        if not self.data_in_memory:
            return []
        if self.first_key_in_memory <= start:
            # We'll serve it from memory
            for key, value in self.data_in_memory:
                if key < start:
                    continue
                if key > stop:
                    return
                yield key, value
        else:
            it = self.db_storage.iterate(start)
            try:
                for key, value in it:
                    if key < start:
                        continue
                    if key > stop:
                        return
                    yield key, value
                # We must iterate from the memory
                if self.data_in_memory:
                    yield from self.get_archive(self.first_key_in_memory, stop)
            finally:
                try_close(it)

    def get_latest_value(self) -> KVTuple:
        """
        Get the piece of data that was added here last

        :return: a tuple of (key, value)
        :raise ValueError: no data in series
        """
        if self.stop_entry is None:
            raise ValueError('No data in series')
        if self.data_in_memory:
            return self.data_in_memory[-1]
        else:
            iterator = self.db_storage.iterate(self.stop_entry)
            try:
                return next(iterator)
            finally:
                iterator.close()

    @RMonitor.synchronized
    def cleanup_keep_in_memory(self) -> None:
        """
        Eject values from memory that should reside in the DB onto the DB
        """
        first_key = self.first_key_in_memory
        if first_key is None:
            return
        cutoff_point = self.stop_entry - self.span_to_keep_in_memory
        for index, row in enumerate(self.data_in_memory):
            ts, value = row
            if ts > cutoff_point:
                for ts, value in self.data_in_memory[:index]:
                    self.db_storage.put(ts, value)
                del self.data_in_memory[:index]
                break
        else:
            self.sync_to_db()
            self.data_in_memory = []
            return

    @RMonitor.synchronized
    def cleanup_keep_in_db(self) -> None:
        """
        Clear up the database to conform to our span_to_keep_in_db
        """
        if self.start_entry is None or not self.data_in_memory:
            return
        cutoff_span = self.stop_entry - self.span_to_keep_in_db
        if self.start_entry == self.first_key_in_memory:
            # The entire series is loaded in the memory
            self.data_in_memory = [tpl for tpl in self.data_in_memory if tpl[0] >= cutoff_span]
            if self.data_in_memory:
                self.start_entry = self.first_key_in_memory
            else:
                self.start_entry = self.stop_entry = None
        else:
            if not self._cleanup_the_db():
                return
            self.cleanup_keep_in_db()

    def on_new_data(self, key: K, value: V) -> None:
        """
        Called by the user when there's new data gathered.

        Key must be greater than start entry

        :param key: key of the new data
        :param value: value of the new data
        :raise ValueError: key was not larger than current stop entry
        """
        if self.stop_entry is not None:
            if key <= self.stop_entry:
                raise ValueError('Key not greater than current stop entry!')

        self.data_in_memory.append((key, value))
        self.stop_entry = key
        if self.start_entry is None:
            self.start_entry = key

    def on_sync_request(self, maximum_entries: tp.Optional[int] = math.inf) -> tp.Iterator[KVTuple]:
        """
        Return an iterator that will provide the source of the data for synchronization.

        This will preferentially start from the first value, so as to keep values synchronized
        in-order.

        :param maximum_entries:
        :return: an iterator of (KVTuple) that should be synchronized against the server
        :raise ValueError: nothing to synchronize!
        """
        if not self.start_entry:
            raise ValueError('Nothing to synchronize!')
        if self.synced_up_to == self.data_in_memory[-1][0]:
            raise ValueError('Nothing to synchronize!')
        if self.synced_up_to is None:
            # Sync everything
            iterator = self.db_storage.iterate(None)
            try:
                data = list(iterator)
                if len(data) < maximum_entries:
                    entries_left = maximum_entries - len(data)
                    if entries_left == math.inf:
                        data = itertools.chain(data, self.data_in_memory)
                    else:
                        data = itertools.chain(data, self.data_in_memory[:entries_left])
                return data
            finally:
                try_close(iterator)
        else:
            if self.first_key_in_memory <= self.synced_up_to:
                # Means we have to sync from memory
                if self.synced_up_to is None:
                    return self.data_in_memory
                else:
                    index = bisect.bisect_right([y[0] for y in self.data_in_memory],
                                                self.synced_up_to)
                    if maximum_entries == math.inf:
                        return self.data_in_memory[index:]
                    else:
                        return self.data_in_memory[index:index + maximum_entries]
            else:
                # We have to start off the disk
                data = []
                iterator = self.db_storage.iterate(self.start_entry)
                try:
                    while len(data) < maximum_entries:
                        try:
                            data.append(next(iterator))
                        except StopIteration:
                            for index, tpl in enumerate(self.data_in_memory):
                                if len(data) >= maximum_entries:
                                    break
                                if self.synced_up_to is not None:
                                    if tpl[0] > self.synced_up_to:
                                        break
                            return itertools.chain(data, self.data_in_memory[:index])
                    else:
                        return data
                finally:
                    try_close(iterator)

    def on_synced_up_to(self, key: K) -> None:
        """
        Called when data was successfully synced up to key included

        :param key: maximum key synchronized
        """
        self.synced_up_to = key

    @property
    def first_key_in_memory(self) -> tp.Optional[K]:
        """
        :return: key of the first element stored in memory
        """
        if not self.data_in_memory:
            return None
        else:
            return self.data_in_memory[0][0]
