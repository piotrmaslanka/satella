import copy
import typing as tp

from satella.coding.recast_exceptions import rethrow_as
from satella.exceptions import ConfigurationValidationError
from .base import Descriptor, must_be_type, ConfigDictValue
from .registry import register_custom_descriptor


@register_custom_descriptor('list', is_plain=False)
class List(Descriptor):
    """
    This must be a list, made of entries of a descriptor (this is optional)
    """
    __slots__ = ('type_descriptor',)

    CHECKERS = [must_be_type(list, tuple)]
    BASIC_MAKER = list

    def __init__(self, type_descriptor: tp.Optional[Descriptor] = None):
        super().__init__()
        self.type_descriptor = type_descriptor or Descriptor()  # type: Descriptor

    def __call__(self, value: ConfigDictValue) -> tp.List:
        value = super().__call__(value)

        return [self.type_descriptor(p) for p in value]

    def __str__(self):
        return 'List(%s)' % (self.type_descriptor,)


DictDescriptorKey = tp.NewType('DictDescriptorKey', Descriptor)


def create_key(descriptor: Descriptor, name: str, optional: bool = False,
               default: tp.Optional[tp.Any] = None) -> DictDescriptorKey:
    descriptor.name = name
    descriptor.optional = optional
    descriptor.default = default

    return descriptor


@register_custom_descriptor('caster', is_plain=False)
class Caster(Descriptor):
    """
    A value must be ran through a function.

    Use like:

    >>> class Environment(enum.IntEnum):
    >>>     PRODUCTION = 0
    >>> assert Caster(Environment)(0) == Environment.PRODUCTION
    """

    def __init__(self, to_cast: tp.Callable[[tp.Any], tp.Any]):
        self.to_cast = to_cast

    @rethrow_as(ValueError, ConfigurationValidationError)
    def __call__(self, value: ConfigDictValue):
        return self.to_cast(value)


@register_custom_descriptor('dict', is_plain=False)
class Dict(Descriptor):
    """
    This entry must be a dict, having at least specified keys.

    Use like:

    >>> Dict([
    >>>     create_key(String(), 'key_s'),
    >>>     create_key(Integer(), 'key_i'),
    >>>     create_key(Float(), 'key_f'),
    >>>     create_key(String(), 'key_not_present', optional=True,
    >>>                default='hello world'),
    >>>     create_key(IPv4(), 'ip_addr')
    >>>])
    """
    __slots__ = ('keys', 'unknown_key_mapper')

    BASIC_MAKER = dict
    CHECKERS = [must_be_type(dict)]

    UnknownKeyHandlerType = tp.Callable[[str, ConfigDictValue], tp.Any]

    def __init__(self, keys: tp.List[DictDescriptorKey],
                 unknown_key_mapper: UnknownKeyHandlerType = lambda str,
                                                                    data: data):
        super().__init__()
        self.keys = {item.name: item for item in keys}  # type: tp.Dict[str, DictDescriptorKey]
        self.unknown_key_mapper = unknown_key_mapper  # Dict.UnknownKeyHandlerType

    def __str__(self):
        return 'Dict(%s)' % (self.keys,)

    def __call__(self, value: ConfigDictValue) -> dict:
        value = copy.copy(value)
        if not isinstance(value, dict):
            raise ConfigurationValidationError('value passed was not a dict: %s' % (value,))
        value = super().__call__(value)

        if not isinstance(value, dict):
            raise ConfigurationValidationError('value received from descriptor was not a dict: %s'
                                               % (value,))

        output = {}

        for key, key_descriptor in self.keys.items():
            try:
                v = value.pop(key)
            except KeyError:
                if key_descriptor.optional:
                    output[key] = key_descriptor.default
                else:
                    raise ConfigurationValidationError('required key %s not found' % (key,))
            else:
                output[key] = key_descriptor(v)

        for k, v in value.items():
            output[k] = self.unknown_key_mapper(k, v)

        return output


@register_custom_descriptor('union', is_plain=False)
class Union(Descriptor):
    """
    The type of one of the child descriptors. If posed as such:

    Union(List(), Dict())

    then value can be either a list or a dict
    """
    __slots__ = ('descriptors',)

    def __init__(self, *descriptors: tp.List[Descriptor]):
        super().__init__()
        self.descriptors = descriptors

    def __call__(self, value: tp.Any) -> tp.Any:
        for descriptor in self.descriptors:
            try:
                return descriptor(value)
            except ConfigurationValidationError:
                continue
        raise ConfigurationValidationError('Could not match value %s to a descriptor' % (value,))
