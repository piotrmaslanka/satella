import copy
import typing as tp

from satella.coding.recast_exceptions import rethrow_as
from satella.configuration.schema import Descriptor, descriptor_from_dict
from satella.exceptions import ConfigurationValidationError

T = tp.TypeVar('T')


class DictObject(tp.MutableMapping[str, T]):
    """
    A dictionary wrapper that can be accessed by attributes.

    You can use keys different than strings, but they will be inaccessible as attributes, and
    you will have to do subscription to get them.

    Eg:

    >>> a = DictObject({'test': 5})
    >>> self.assertEqual(a.test, 5)
    """

    def __init__(self, *args, **kwargs):
        self.__data = dict(*args, **kwargs)

    def __delitem__(self, k: str) -> None:
        del self.__data[k]

    def __setitem__(self, k: str, v: T) -> None:
        self.__data[k] = v

    def __getitem__(self, item: str) -> T:
        return self.__data[item]

    def __iter__(self) -> tp.Iterator[str]:
        return iter(self.__data)

    def __len__(self) -> int:
        return len(self.__data)

    def __copy__(self) -> 'DictObject':
        return DictObject(self.__data.copy())

    def __eq__(self, other: dict):
        if isinstance(other, DictObject):
            return self.__data == other.__data
        else:
            return self.__data == other

    def copy(self) -> 'DictObject':
        return DictObject(self.__data.copy())

    def __deepcopy__(self, memo) -> 'DictObject':
        return DictObject(copy.deepcopy(self.__data, memo))

    @rethrow_as(KeyError, AttributeError)
    def __getattr__(self, item: str) -> T:
        return self[item]

    def __setattr__(self, key: str, value: T) -> None:
        if key == '_DictObject__data':
            return super().__setattr__(key, value)
        else:
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
            descriptor(self.__data)
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