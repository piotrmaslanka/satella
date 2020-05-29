import collections
import time
import typing as tp
import threading
import weakref

from ..singleton import Singleton
from ...concurrent.monitor import Monitor
from ...recast_exceptions import rethrow_as
from ..structures import TimeBasedSetHeap

K, V = tp.TypeVar('K'), tp.TypeVar('V')


@Singleton
class ExpiringEntryDictThread(threading.Thread, Monitor):
    """A background thread providing maintenance for expiring entry dicts"""
    def __init__(self):
        super().__init__(name='ExpiringEntryDict cleanup thread', daemon=True)
        Monitor.__init__(self)
        self.entries = []
        self.started = False

    def start(self):
        if self.started:
            return

        self.started = True
        super().start()

    def run(self):
        while True:
            time.sleep(5)
            with Monitor.acquire(self):
                new_entries = []
                for index, ref in enumerate(self.entries):
                    obj = ref()
                    if obj is not None:
                        obj.cleanup()
                        new_entries.append(ref)
                self.entries = new_entries

    @Monitor.synchronized
    def add_dict(self, ed):
        self.entries.append(weakref.ref(ed))
        self.start()


class SelfCleaningDefaultDict(Monitor, collections.UserDict, tp.Generic[K, V]):
    """
    A defaultdict with the property that if it detects that a value is equal to it's default value,
    it will automatically remove it from the dict.

    It is preferable to :py:meth:`satella.coding.concurrent.Monitor.acquire` it before iterating, since
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
            del self[key]

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
    def cleanup(self):
        for key in list(self.data.keys()):
            if self.data[key] == self.default_value:
                del self.data[key]


class ExpiringEntryDict(Monitor, collections.UserDict, tp.Generic[K, V]):
    """
    A dictionary whose entries expire automatically after a predefined period of time.

    Note that cleanup is invoked only when iterating over the dicts, or automatically if you specify
    external_cleanup to be True.

    Note that it's preferential to :py:meth:`satella.coding.concurrent.Monitor.acquire` it if you're
    using an external cleanup thread, because the dict may mutate at any time.

    :param expiration_timeout: number of seconds after which entries will expire
    :param time_getter: a callable/0 that returns the current timestamp
    :param external_cleanup: whether to spawn a single thread that will clean up the dictionary.
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
