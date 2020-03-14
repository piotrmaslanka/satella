import collections.abc
import copy
import typing as tp

from satella.coding.recast_exceptions import rethrow_as
from satella.configuration.schema import Descriptor, descriptor_from_dict
from satella.exceptions import ConfigurationValidationError
from ..decorators import for_argument

__all__ = ['DictObject', 'apply_dict_object', 'DictionaryView', 'TwoWayDictionary']

K, V, T = tp.TypeVar('K'), tp.TypeVar('V'), tp.TypeVar('T')


class DictObject(dict, tp.Generic[T]):
    """
    A dictionary wrapper that can be accessed by attributes. Eg:

    >>> a = DictObject({'test': 5})
    >>> self.assertEqual(a.test, 5)
    """

    def __copy__(self) -> 'DictObject':
        return DictObject(copy.copy(dict(self)))

    def __deepcopy__(self, memodict={}) -> 'DictObject':
        return DictObject(copy.deepcopy(dict(self), memo=memodict))

    @rethrow_as(KeyError, AttributeError)
    def __getattr__(self, item: str) -> T:
        return self[item]

    def __setattr__(self, key: str, value: T) -> None:
        self[key] = value

    @rethrow_as(KeyError, AttributeError)
    def __delattr__(self, key: str) -> None:
        del self[key]

    def is_valid_schema(self, schema: tp.Optional[tp.Union[Descriptor, tp.Dict]] = None,
                        **kwarg_schema) -> bool:
        """
        Check if this dictionary conforms to particular schema.

        Schema is either a Descriptor, or a JSON-based schema. See satella.configuration.schema for details.
        Schema can be passed as well using kwargs. It will be preferred to the one passed as schema.

        :param schema: schema to verify against
        :return: whether is conformant
        """

        if kwarg_schema:
            schema = kwarg_schema

        if isinstance(schema, Descriptor):
            descriptor = schema
        else:
            descriptor = descriptor_from_dict(schema)

        try:
            descriptor(self)
        except ConfigurationValidationError:
            return False
        else:
            return True


def apply_dict_object(v: tp.Union[tp.Any, tp.Dict[str, T]]) -> tp.Union[DictObject, tp.Any]:
    """
    Apply DictObject() to every dict inside v.

    This assumes that the only things that will be touched will be nested dicts and lists.

    If you pass a non-dict and a non-list, they will be returned as is.
    """
    if isinstance(v, list):
        return [apply_dict_object(x) for x in v]
    elif isinstance(v, dict):
        return DictObject({
            k: apply_dict_object(val) for k, val in v.items()
        })
    else:
        return v


class DictionaryView(collections.abc.MutableMapping, tp.Generic[K, V]):
    """
    A view on a multiple dictionaries. If key isn't found in the first dictionary, it is looked up
    in another. Use like:

    >>> dv = DictionaryView({1:2, 3:4}, {4: 5, 6: 7})
    >>> assert dv[4] == 5
    >>> del dv[1]
    >>> assertRaises(KeyError, lambda: dv.__delitem__(1))

    :param master_dict: First dictionary to look up. Entries made via __setitem__ will be put here.
    :param rest_of_dicts: Remaining dictionaries
    :param propagate_deletes: Whether to delete given key from the first dictionary that it is
        found. Otherwise it will be only deleted from the master_dict. Also, if this is set to
        False, on deletion, if the key isn't found in master dictionary, deletion will KeyError.
    :param assign_to_same_dict: whether updates done by __setitem__ should be written to the
        dictionary that contains that key. If not, all updates will be stored in master_dict. If
        this is True, updates made to keys that are not in this dictionary will go to master_dict.
    """
    __slots__ = ('assign_to_same_dict', 'master_dict', 'dictionaries', 'propagate_deletes')

    def __copy__(self):
        return DictionaryView(*copy.copy(self.dictionaries))

    def __deepcopy__(self, memodict={}):
        return DictionaryView(*copy.deepcopy(self.dictionaries, memo=memodict))

    def __init__(self, master_dict: tp.Dict[K, V], *rest_of_dicts: tp.Dict[K, V],
                 propagate_deletes: bool = True,
                 assign_to_same_dict: bool = True):
        self.assign_to_same_dict = assign_to_same_dict
        self.master_dict = master_dict
        self.dictionaries = [master_dict, *rest_of_dicts]
        self.propagate_deletes = propagate_deletes

    @for_argument(returns=list)
    def keys(self) -> tp.AbstractSet[K]:
        """
        Returns all keys found in this view
        """
        seen_already = set()
        for dictionary in self.dictionaries:
            for key in dictionary:
                if key not in seen_already:
                    yield key
                    seen_already.add(key)

    @for_argument(returns=list)
    def values(self) -> tp.AbstractSet[V]:
        seen_already = set()
        for dictionary in self.dictionaries:
            for key, value in dictionary.items():
                if key not in seen_already:
                    yield value
                    seen_already.add(key)

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

    @for_argument(returns=list)
    def items(self) -> tp.AbstractSet[tp.Tuple[K, V]]:
        seen_already = set()
        for dictionary in self.dictionaries:
            for key, value in dictionary.items():
                if key not in seen_already:
                    yield key, value
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

    def __setitem__(self, key: K, value: V):
        if self.assign_to_same_dict:
            for dictionary in self.dictionaries:
                if key in dictionary:
                    dictionary[key] = value
                    return
        self.master_dict[key] = value

    def __delitem__(self, key: K) -> V:
        if self.propagate_deletes:
            for dictionary in self.dictionaries:
                if key in dictionary:
                    del dictionary[key]
                    return
            raise KeyError('Key not found')
        else:
            del self.master_dict[key]


class TwoWayDictionary(collections.abc.MutableMapping, tp.Generic[K, V]):
    """
    A dictionary that keeps also a reverse_data mapping, allowing to look up keys by values.

    Not thread-safe.

    Example usage:

    >>> twd = TwoWayDictionary()
    >>> twd[2] = 3
    >>> self.assertEqual(twd.reverse[3], 2)

    :param data: data to generate the dict from
    :raises ValueError: on being given data from which it is impossible to construct a reverse
        mapping (ie. same value appears at least twice)
    """
    __slots__ = ('data', 'reverse_data', '_reverse')

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

    def __getitem__(self, item: K) -> V:
        return self.data[item]

    def items(self) -> tp.Iterator[tp.Tuple[K, V]]:
        return self.data.items()

    def keys(self) -> tp.AbstractSet[K]:
        return self.data.keys()

    def values(self) -> tp.AbstractSet[V]:
        return self.data.values()

    def __len__(self) -> int:
        return len(self.data)

    def __setitem__(self, key: K, value: V):
        if value in self.reverse_data:
            raise ValueError('This value is already mapped to something!')

        try:
            prev_val = self.data[key]
        except KeyError:
            pass
        else:
            del self.reverse_data[prev_val]

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
