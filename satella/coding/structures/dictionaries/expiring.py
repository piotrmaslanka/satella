import threading
import time
import typing as tp
import weakref
from abc import ABCMeta, abstractmethod

from ..heaps import TimeBasedSetHeap
from ..singleton import Singleton
from ...concurrent.monitor import Monitor
from ...recast_exceptions import rethrow_as, silence_excs

K, V = tp.TypeVar('K'), tp.TypeVar('V')


class Cleanupable(metaclass=ABCMeta):
    @abstractmethod
    def cleanup(self) -> None:
        ...


@Singleton
class ExpiringEntryDictThread(threading.Thread, Monitor):
    """
    A background thread providing maintenance for expiring entry dicts
    and self-cleaning default dicts
    """

    def __init__(self):
        super().__init__(name='ExpiringEntryDict cleanup thread', daemon=True)
        Monitor.__init__(self)
        self.entries = []  # type: tp.List[weakref.ref[Cleanupable]]
        self.started = False  # type: bool

    def start(self) -> None:
        if self.started:
            return

        self.started = True
        super().start()

    def run(self) -> None:
        while True:
            time.sleep(5)
            self.cleanup()

    @Monitor.synchronized
    def cleanup(self) -> None:
        new_entries = []
        for index, ref in enumerate(self.entries):
            obj = ref()
            if obj is not None:
                obj.cleanup()
                new_entries.append(ref)
        self.entries = new_entries

    @Monitor.synchronized
    def add_dict(self, ed: Cleanupable) -> None:
        self.entries.append(weakref.ref(ed))
        self.start()


class SelfCleaningDefaultDict(Monitor, tp.MutableMapping[K, V], Cleanupable):
    """
    A defaultdict with the property that if it detects that a value is equal to it's default value,
    it will automatically remove it from the dict.

    Please note that this will spawn a cleanup thread in the background, one per program. The thread
    is shared between :class:`satella.coding.structures.SelfCleaningDefaultDict` and
    :class:`satella.coding.structures.ExpiringEntryDict`

    It is preferable to :meth:`satella.coding.concurrent.Monitor.acquire` it before iterating, since
    it is cleaned up both by __iter__ and by an external worker thread, so it's important to acquire
    it, because it can mutate in an undefined way.

    Note that if you access a key which does not exist, and background_maintenance is False,
    a default value will be created and inserted into the dictionary. This is the only
    time that the dictionary will hold values that are equal to default.

    :param default_factory: a callable/0 that will return an object if it doesn't already exist
    :param background_maintenance: whether to spawn a background thread. This is required
        if dictionary values can change their value between inserts.

    All args and kwargs will be passed to a dict, which will be promptly added to this dictionary.
    """

    def __len__(self) -> int:
        self.cleanup()
        return len(self.data)

    def __init__(self, default_factory: tp.Callable[[], V],
                 background_maintenance: bool = True, *args, **kwargs):
        super().__init__()  # initialize the inner Monitor
        self.data = dict(*args, **kwargs)
        self.default_factory = default_factory
        self.default_value = default_factory()

        self.background_maintenance = background_maintenance
        if self.background_maintenance:
            ExpiringEntryDictThread().add_dict(self)

    def __iter__(self) -> tp.Iterator[K]:
        self.cleanup()
        return super().__iter__()

    def __delitem__(self, key: K) -> None:
        if key in self.data:
            del self.data[key]

    @Monitor.synchronized
    def __getitem__(self, item: K) -> V:
        try:
            v = self.data[item]
            if v == self.default_value:
                del self.data[item]
            return v
        except KeyError:
            obj = self.default_factory()
            if not self.background_maintenance:
                self.data[item] = obj
            return obj

    @Monitor.synchronized
    def __setitem__(self, key: K, value: V) -> None:
        value_equal = value == self.default_value
        if key in self.data:
            if value_equal:
                del self.data[key]

        if not value_equal:
            self.data[key] = value

    @Monitor.synchronized
    @silence_excs(KeyError)  # because entries may disappear without warning
    def cleanup(self) -> None:
        for key in list(self.data.keys()):
            if self.data[key] == self.default_value:
                del self.data[key]


class ExpiringEntryDict(Monitor, tp.MutableMapping[K, V], Cleanupable):
    """
    A dictionary whose entries expire automatically after a predefined period of time.

    Note that cleanup is invoked only when iterating over the dicts, or automatically if you specify
    external_cleanup to be True each approximately 5 seconds.

    Note that it's preferential to :meth:`satella.coding.concurrent.Monitor.acquire` it if you're
    using an external cleanup thread, because the dict may mutate at any time.

    :param expiration_timeout: number of seconds after which entries will expire
    :param time_getter: a callable/0 that returns the current timestamp
    :param external_cleanup: whether to spawn a single thread that will clean up the dictionary.
        The thread is spawned once per program, and no additional threads are spawned for next
        dictionaries.

    All args and kwargs will be passed to a dict, which will be promptly added to this dictionary.
    """

    def __len__(self) -> int:
        self.cleanup()
        return len(self.data)

    def __init__(self, expiration_timeout: float, *args,
                 time_getter: tp.Callable[[], float] = time.monotonic,
                 external_cleanup: bool = False, **kwargs):
        super().__init__()  # initialize the inner Monitor
        self.data = dict()
        self.expire_on = {}
        self.time_getter = time_getter
        self.expiration_timeout = expiration_timeout
        self.key_to_expiration_time = TimeBasedSetHeap()

        if external_cleanup:
            ExpiringEntryDictThread().add_dict(self)

        dct = dict(*args, **kwargs)
        for key, value in dct.items():
            self[key] = value

    def __contains__(self, item) -> bool:
        try:
            ts = self.key_to_expiration_time.item_to_timestamp[item]
        except KeyError:
            return False

        if ts < self.time_getter():
            del self[item]
            return False

        return True

    def get_timestamp(self, key: K) -> float:
        """
        Return the timestamp at which given key was inserted in the dict

        :raises KeyError: key not found in the dictionary
        """
        return self.key_to_expiration_time.item_to_timestamp[key]

    def __iter__(self) -> tp.Iterator[K]:
        self.cleanup()
        return super().__iter__(self)

    @Monitor.synchronized
    def cleanup(self) -> None:
        """Remove entries that are later than given time"""
        for ts, key in self.key_to_expiration_time.pop_less_than(self.time_getter()):
            del self.data[key]

    @Monitor.synchronized
    def __setitem__(self, key: K, value: V) -> None:
        self.key_to_expiration_time.put(self.time_getter() + self.expiration_timeout, key)
        self.data[key] = value

    @rethrow_as(ValueError, KeyError)
    def __getitem__(self, item: K) -> V:
        ts = self.key_to_expiration_time.get_timestamp(item)
        if ts < self.time_getter():
            del self.data[item]
            raise KeyError('Entry expired')

        return self.data[item]

    @Monitor.synchronized
    def __delitem__(self, key: K) -> None:
        self.key_to_expiration_time.pop_item(key)
        del self.data[key]
