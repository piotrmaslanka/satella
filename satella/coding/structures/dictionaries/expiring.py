import collections
import time
import typing as tp
import threading
import weakref
from abc import ABCMeta, abstractmethod

from ..singleton import Singleton
from ...concurrent.monitor import Monitor
from ...recast_exceptions import rethrow_as, silence_excs
from ..heaps import TimeBasedSetHeap

K, V = tp.TypeVar('K'), tp.TypeVar('V')


class Cleanupable(metaclass=ABCMeta):
    @abstractmethod
    def cleanup(self):
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
        self.entries = []       # type: tp.List[weakref.ref[Cleanupable]]
        self.started = False    # type: bool

    def start(self):
        if self.started:
            return

        self.started = True
        super().start()

    def run(self):
        while True:
            time.sleep(5)
            self.cleanup()

    @Monitor.synchronized
    def cleanup(self):
        new_entries = []
        for index, ref in enumerate(self.entries):
            obj = ref()
            if obj is not None:
                obj.cleanup()
                new_entries.append(ref)
        self.entries = new_entries

    @Monitor.synchronized
    def add_dict(self, ed: Cleanupable):
        self.entries.append(weakref.ref(ed))
        self.start()


class SelfCleaningDefaultDict(Monitor, collections.UserDict, tp.Generic[K, V], Cleanupable):
    """
    A defaultdict with the property that if it detects that a value is equal to it's default value,
    it will automatically remove it from the dict.

    Please note that this will spawn a cleanup thread in the background, one per program. The thread
    is shared between :class:`satella.coding.structures.SelfCleaningDefaultDict` and
    :class:`satella.coding.structures.ExpiringEntryDict`

    It is preferable to :meth:`satella.coding.concurrent.Monitor.acquire` it before iterating, since
    it is cleaned up both by __iter__ and by an external worker thread, so it's important to acquire
    it, because it can mutate in an undefined way.
    """
    def __init__(self, default_factory: tp.Callable[[], V], *args, **kwargs):
        super().__init__()
        collections.UserDict.__init__(self, *args, **kwargs)
        self.default_factory = default_factory
        self.default_value = default_factory()

        ExpiringEntryDictThread().add_dict(self)

    def __iter__(self) -> tp.Iterator[K]:
        self.cleanup()
        return super().__iter__()

    def __delitem__(self, key: K):
        if key in self.data:
            del self.data[key]

    def __getitem__(self, item: K) -> V:
        if item not in self.data:
            self.data[item] = self.default_factory()
        return self.data[item]

    def __setitem__(self, key: K, value: V):
        if key in self.data:
            if value == self.default_value:
                del self.data[key]
        self.data[key] = value

    @Monitor.synchronized
    @silence_excs(KeyError)     # because entries may disappear without warning
    def cleanup(self):
        for key in list(self.data.keys()):
            if self.data[key] == self.default_value:
                del self.data[key]


class ExpiringEntryDict(Monitor, collections.UserDict, tp.Generic[K, V], Cleanupable):
    """
    A dictionary whose entries expire automatically after a predefined period of time.

    Note that cleanup is invoked only when iterating over the dicts, or automatically if you specify
    external_cleanup to be True each approximately 5 seconds.

    Note that it's preferential to :meth:`satella.coding.concurrent.Monitor.acquire` it if you're
    using an external cleanup thread, because the dict may mutate at any time.

    :param expiration_timeout: number of seconds after which entries will expire
    :param time_getter: a callable/0 that returns the current timestamp
    :param external_cleanup: whether to spawn a single thread that will clean up the dictionary.
        The thread is spawned once per program, and no additional threads are spawned for next dictionaries.
    """
    def __init__(self, expiration_timeout: float, *args, time_getter: tp.Callable[[], float] = time.monotonic,
                 external_cleanup: bool = False, **kwargs):
        super().__init__()
        self.expire_on = {}
        self.time_getter = time_getter
        self.expiration_timeout = expiration_timeout
        self.key_to_expiration_time = TimeBasedSetHeap()

        if external_cleanup:
            ExpiringEntryDictThread().add_dict(self)

        collections.UserDict.__init__(self, *args, **kwargs)

    def __contains__(self, item):
        try:
            ts = self.key_to_expiration_time.item_to_timestamp[item]
        except KeyError:
            return False

        if ts < self.time_getter():
            del self[item]
            return False

        return True

    def __iter__(self) -> tp.Iterator[K]:
        self.cleanup()
        return super().__iter__(self)

    @Monitor.synchronized
    def cleanup(self):
        """Remove entries that are later than given time"""
        for ts, key in self.key_to_expiration_time.pop_less_than(self.time_getter()):
            del self.data[key]

    def __setitem__(self, key: K, value: V):
        self.key_to_expiration_time.put(self.time_getter()+self.expiration_timeout, key)
        super().__setitem__(key, value)

    @rethrow_as(ValueError, KeyError)
    def __getitem__(self, item: K):
        ts = self.key_to_expiration_time.get_timestamp(item)
        if ts < self.time_getter():
            del self[item]
            raise KeyError('Entry expired')

        return super().__getitem__(item)

    def __delitem__(self, key: K):
        self.key_to_expiration_time.pop_item(key)
        super().__delitem__(key)
