from __future__ import annotations
import copy
import typing as tp
import warnings

from satella.coding.typing import K, V


class DirtyDict(tp.MutableMapping[K, V]):
    """
    A dictionary that has also a flag called .dirty that sets to True if the dictionary has been
    changed since that flag was last cleared.

    Setting the dict with the value that it already has doesn't count as dirtying it.
    Note that such changes will not be registered in the dict!

    All arguments and kwargs will be passed to dict's constructor.
    """

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> tp.Iterator[K]:
        return iter(self.data)

    def __getitem__(self, k: K) -> V:
        return self.data[k]

    def __init__(self, *args, **kwargs):
        self.data = dict(*args, **kwargs)  # type: tp.Dict[K, V]
        self.dirty = False

    def __copy__(self) -> 'DirtyDict':
        dd = DirtyDict(self.data.copy())
        dd.dirty = self.dirty
        return dd

    def __setitem__(self, key: K, value: V) -> None:
        if key in self.data:
            if self.data[key] == value:
                return
        self.data[key] = value
        self.dirty = True

    def __delitem__(self, key: K) -> None:
        del self.data[key]
        self.dirty = True

    def __contains__(self, item: K) -> bool:
        return item in self.data

    def clear_dirty(self) -> None:
        """Clears the dirty flag"""
        self.dirty = False

    def __bool__(self) -> bool:
        return bool(self.data)

    def swap_and_clear_dirty(self) -> tp.Dict[K, V]:
        """
        Returns this data, clears self and sets dirty to False

        After this is called, this dict will be considered empty.

        :return: a plain, normal Python dictionary is returned
        """
        a = self.data
        self.data = {}
        self.dirty = False
        return a

    def copy_and_clear_dirty(self) -> tp.Dict[K, V]:
        """
        Returns a copy of this data and sets dirty to False

        :return: a plain, normal Python dictionary is returned
        """
        a = self.data.copy()
        self.dirty = False
        return a


class KeyAwareDefaultDict(tp.MutableMapping[K, V]):
    """
    A defaultdict whose factory function accepts the key to provide a default value for the key

    :param factory_function: a callable that accepts a single argument, a key, for which it is
        to provide a default value
    """

    def __len__(self) -> int:
        return len(self.dict)

    def __iter__(self) -> tp.Iterator[K]:
        return iter(self.dict)

    def __init__(self, factory_function: tp.Callable[[K], V], *args, **kwargs):
        self.dict = dict(*args, **kwargs)
        self.factory_function = factory_function

    def __getitem__(self, item: K) -> V:
        if item in self.dict:
            return self.dict[item]
        self.dict[item] = self.factory_function(item)
        return self.dict[item]

    def __setitem__(self, key: K, value: V) -> None:
        self.dict[key] = value

    def __delitem__(self, key: K) -> None:
        del self.dict[key]


class TwoWayDictionary(tp.MutableMapping[K, V]):
    """
    A dictionary that keeps also a reverse_data mapping, allowing to look up keys by values.

    Not thread-safe.

    Example usage:

    >>> twd = TwoWayDictionary()
    >>> twd[2] = 3
    >>> self.assertEqual(twd.reverse[3], 2)

    When you're done using a given TwoWayDictionary, please call .done(). This will make it easier
    for the GC to collect
    the dictionaries.

    You can also use the context manager to make the TwoWayDictionary clean up itself, eg.

    >>> with TwoWayDictionary() as twd:
    >>>     ...
    >>> # at this point twd is .done()

    :param data: data to generate the dict from
    :raises ValueError: on being given data from which it is impossible to construct a reverse
        mapping (ie. same value appears at least twice)
    """
    __slots__ = 'data', 'reverse_data', '_reverse'

    def done(self) -> None:
        """
        Called when the user is done using given TwoWayDictionary.

        Internally this will break the reference cycle, and enable Python GC to collect the objects.
        """
        self.reverse.reverse = None
        self.reverse = None

    def __init__(self, data=None, _is_reverse: bool = False):
        if not _is_reverse:
            self.data = dict(data or [])
            self.reverse_data = {v: k for k, v in self.data.items()}
            if len(self.reverse_data) != len(self.data):
                raise ValueError('Value repeats itself, invalid data!')

            self._reverse = TwoWayDictionary(_is_reverse=True)
            self._reverse.data = self.reverse_data
            self._reverse.reverse_data = self.data
            self._reverse._reverse = self

    def __enter__(self) -> TwoWayDictionary:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.done()
        return False

    def __getitem__(self, item: K) -> V:
        return self.data[item]

    def __len__(self) -> int:
        return len(self.data)

    def __setitem__(self, key: K, value: V) -> None:
        if value in self.reverse_data:
            raise ValueError('This value is already mapped to something!')

        try:
            prev_val = self.data[key]
            del self.reverse_data[prev_val]
        except KeyError:
            pass

        self.data[key] = value
        self.reverse_data[value] = key

    def __delitem__(self, key: K) -> None:
        value = self.data[key]
        del self.data[key]
        del self.reverse_data[value]

    def __iter__(self) -> tp.Iterator[K]:
        return iter(self.data)

    @property
    def reverse(self) -> tp.MutableMapping[V, K]:
        """
        Return a reverse mapping. Reverse mapping is updated as soon as an operation is done.
        """
        return self._reverse


class DictionaryView(tp.MutableMapping[K, V]):
    """
    A view on a multiple dictionaries. If key isn't found in the first dictionary, it is looked up
    in another. Use like:

    >>> dv = DictionaryView({1:2, 3:4}, {4: 5, 6: 7})
    >>> assert dv[4] == 5
    >>> del dv[1]
    >>> assertRaises(KeyError, lambda: dv.__delitem__(1))

    .. deprecated:: 2.14.22
       Use ChainMap_ instead.

    .. _ChainMap: https://docs.python.org/3/library/collections.html#collections.ChainMap

    :param master_dict: First dictionary to look up. Entries made via __setitem__ will be put here.
    :param rest_of_dicts: Remaining dictionaries
    :param propagate_deletes: Whether to delete given key from the first dictionary that it is
        found. Otherwise it will be only deleted from the master_dict. Also, if this is set to
        False, on deletion, if the key isn't found in master dictionary, deletion will KeyError.
    :param assign_to_same_dict: whether updates done by __setitem__ should be written to the
        dictionary that contains that key. If not, all updates will be stored in master_dict. If
        this is True, updates made to keys that are not in this dictionary will go to master_dict.
    """
    __slots__ = 'assign_to_same_dict', 'master_dict', 'dictionaries', 'propagate_deletes'

    def __copy__(self) -> DictionaryView:
        return DictionaryView(*copy.copy(self.dictionaries))

    def __deepcopy__(self, memo) -> 'DictionaryView':
        return DictionaryView(*copy.deepcopy(self.dictionaries, memo=memo))

    def __init__(self, master_dict: tp.Dict[K, V], *rest_of_dicts: tp.Dict[K, V],
                 propagate_deletes: bool = True,
                 assign_to_same_dict: bool = True):
        warnings.warn('This is deprecated and will be removed in Satella 3.0.'
                      'Use collections.ChainMap instead', DeprecationWarning)
        self.assign_to_same_dict = assign_to_same_dict
        self.master_dict = master_dict
        self.dictionaries = [master_dict, *rest_of_dicts]
        self.propagate_deletes = propagate_deletes

    def __contains__(self, item: K) -> bool:
        for dictionary in self.dictionaries:
            if item in dictionary:
                return True
        return False

    def __iter__(self) -> tp.Iterator[K]:
        seen_already = set()
        for dictionary in self.dictionaries:
            for key in dictionary:
                if key not in seen_already:
                    yield key
                    seen_already.add(key)

    def __len__(self) -> int:
        seen_already = set()
        i = 0
        for dictionary in self.dictionaries:
            for key in dictionary:
                if key not in seen_already:
                    i += 1
                    seen_already.add(key)
        return i

    def __getitem__(self, item: K) -> V:
        for dictionary in self.dictionaries:
            if item in dictionary:
                return dictionary[item]
        raise KeyError('Key not found')

    def __setitem__(self, key: K, value: V) -> None:
        if self.assign_to_same_dict:
            for dictionary in self.dictionaries:
                if key in dictionary:
                    dictionary[key] = value
                    return
        self.master_dict[key] = value

    def __delitem__(self, key: K) -> None:
        if self.propagate_deletes:
            for dictionary in self.dictionaries:
                if key in dictionary:
                    del dictionary[key]
                    return
            raise KeyError('Key not found')
        del self.master_dict[key]
