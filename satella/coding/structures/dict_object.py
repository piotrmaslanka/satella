import typing as tp

from satella.configuration.schema import Descriptor, descriptor_from_dict
from satella.exceptions import ConfigurationValidationError

__all__ = ['DictObject', 'apply_dict_object']


class DictObject(dict):
    """
    A dictionary wrapper that can be accessed by attributes. Eg:

    >>> a = DictObject({'test': 5})
    >>> self.assertEqual(a.test, 5)
    """

    def __getattr__(self, item: str) -> tp.Any:
        try:
            return self[item]
        except KeyError as e:
            raise AttributeError(repr(e))

    def __setattr__(self, key: str, value: tp.Any) -> None:
        self[key] = value

    def __delattr__(self, key: str) -> None:
        try:
            del self[key]
        except KeyError as e:
            raise AttributeError(repr(e))

    def is_valid_schema(self, schema: tp.Optional[tp.Union[Descriptor, dict]] = None,
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


def apply_dict_object(v: tp.Any) -> tp.Union[DictObject, tp.Any]:
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
