import copy
import typing as tp

from satella.coding.recast_exceptions import rethrow_as
from satella.configuration.schema import Descriptor, descriptor_from_dict
from satella.exceptions import ConfigurationValidationError


class DictObject(dict):
    """
    A dictionary wrapper that can be accessed by attributes.

    Note that it still remains a completely valid dictionary!

    You can use keys different than strings, but they will be inaccessible as attributes, and
    you will have to do subscription to get them.

    Eg:

    >>> a = DictObject({'test': 5})
    >>> self.assertEqual(a.test, 5)
    >>> self.assertEqual(a['test'], 5)
    """

    def __copy__(self):
        return DictObject(copy.copy(super()))

    def __deepcopy__(self, memo=None):
        return DictObject(copy.deepcopy(super(), memo=memo))

    def __str__(self) -> str:
        return 'DictObject(%s)' % (super().__str__(),)

    def __repr__(self) -> str:
        return 'DictObject(%s)' % (super().__repr__(),)

    @rethrow_as(KeyError, AttributeError)
    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, key, value):
        self[key] = value

    @rethrow_as(KeyError, AttributeError)
    def __delattr__(self, key):
        del self[key]

    def is_valid_schema(self, schema: tp.Optional[tp.Union[Descriptor, tp.Dict]] = None,
                        **kwarg_schema) -> bool:
        """
        Check if this dictionary conforms to particular schema.

        Schema is either a Descriptor, or a JSON-based schema. See satella.configuration.schema
        for details.
        Schema can be passed as well using kwargs. Note that the schema argument will be ignored
        if kwargs are passed.

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


def apply_dict_object(v: tp.Union[tp.Any, tp.Dict]) -> tp.Union[DictObject, tp.Any]:
    """
    Apply DictObject() to every dict inside v.

    This assumes that the only things that will be touched will be nested dicts and lists.

    If you pass a non-dict and a non-list, they will be returned as is.
    """
    if isinstance(v, DictObject):
        return v
    elif isinstance(v, list):
        return [apply_dict_object(x) for x in v]
    elif isinstance(v, dict):
        return DictObject({
            k: apply_dict_object(val) for k, val in v.items()
        })
    else:
        return v
