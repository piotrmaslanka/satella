import collections
import time
import typing as tp

K, V = tp.TypeVar('K'), tp.TypeVar('V')


class LRUDictionary(collections.UserDict, tp.Generic[K, V]):
    """
    A dictionary which holds the timestamp of the last access, and can return the elements with the lowest
    value of this. The timestamp is updated both when an entry is read and written

    """
    def __init__(self, time_getter: tp.Callable[[], float] = time.monotonic):
        self.data = {}                  # type: tp.Dict[K, V]
        self.key_to_timestamps = {}     # type: tp.Dict[K, float]
        self.time_getter = time_getter

    def __getitem__(self, item: K) -> V:
        obj = self.data[item]       # raises KeyError
        self.key_to_timestamps[item] = self.time_getter()
        return obj

    def __setitem__(self, key: K, value: V):
        if key in self.data:
            ts = self.key_to_timestamps[key]
        self.data[key] = value
        self.key_to_timestamps[key] = self.time_getter()

    def __delitem__(self, key):
        del self.data[key]
        del self.key_to_timestamps[key]
