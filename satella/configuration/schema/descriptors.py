import copy
import re
import typing as tp

from satella.coding.concurrent import CallableGroup
from ...exceptions import ConfigurationValidationError, ConfigurationSchemaError

__all__ = [
    'Descriptor',
    'Integer', 'Float', 'String', 'Boolean',
    'IPv4',
    'Regexp',
    'List', 'Dict', 'Union',
    'create_key',
    'must_be_type',
    'must_be_one_of',
    'CheckerCondition',
    'ConfigDictValue',
    'descriptor_from_dict',
    'register_custom_descriptor',
]

ConfigDictValue = tp.Optional[tp.Union[int, float, str, dict, list, bool]]
CheckerConditionType = tp.Callable[[ConfigDictValue], bool]
ObjectMakerType = tp.Callable[
    [ConfigDictValue], tp.Any]  # might raise ConfigurationSchemaError as well


class CheckerCondition(object):
    PRE_CHECKER = 0
    POST_CHECKER = 1

    def __init__(self, conditon: CheckerConditionType, description: str = u'',
                 is_pre_checker: bool = True):
        self.condition = conditon
        self.description = description
        self.is_pre_checker = is_pre_checker

    def __call__(self, value):
        if not self.condition(value):
            raise ConfigurationValidationError(self.description, value)


def must_be_type(*cls_or_tuple):
    return CheckerCondition(conditon=lambda v: isinstance(v, cls_or_tuple),
                            description='not one of types %s' % (cls_or_tuple,))


def must_be_one_of(*items):
    return CheckerCondition(conditon=lambda v: v in items,
                            description='not in set %s' % (items,),
                            is_pre_checker=False)


class Descriptor(object):
    """
    Base class for a descriptor
    """
    BASIC_MAKER = staticmethod(lambda v: v)
    MY_EXCEPTIONS = [TypeError, ValueError]  # a list of Exception classes
    CHECKERS = []  # a list of CheckerCondition

    def __init__(self):
        self.pre_checkers = CallableGroup()
        self.post_checkers = CallableGroup()
        self.name = None
        self.optional = None
        self.default = None

        for checker in self.__class__.CHECKERS:
            self.add_checker(checker)

        self.MY_EXCEPTIONS = tuple(self.MY_EXCEPTIONS)

    def __str__(self):
        return '%s()' % (self.__class__.__qualname__, )

    def __call__(self, value: ConfigDictValue) -> tp.Any:
        """
        raises ConfigurationSchemaError: on invalid schema
        """
        self.pre_checkers(value)

        try:
            value = self.BASIC_MAKER(value)
        except self.MY_EXCEPTIONS as e:
            raise ConfigurationValidationError('could not pass to maker due to %s' % (e, ), value)

        self.post_checkers(value)

        return value

    def add_checker(self, checker: CheckerCondition):
        if checker.is_pre_checker:
            self.pre_checkers.add(checker)
        else:
            self.post_checkers.add(checker)


# noinspection PyDecorator
@staticmethod
def _make_boolean(v: tp.Any) -> bool:
    if isinstance(v, str):
        if v.upper() == 'TRUE':
            return True
        elif v.upper() == 'FALSE':
            return False
        else:
            raise ConfigurationValidationError('Unknown value of "%s" posing to be a bool'
                                               % (v,))
    else:
        return bool(v)


class Boolean(Descriptor):
    """
    This value must be a boolean, or be converted to one
    """
    BASIC_MAKER = _make_boolean


class Integer(Descriptor):
    """
    This value must be an integer, or be converted to one
    """
    BASIC_MAKER = int


class Float(Descriptor):
    """
    This value must be a float, or be converted to one
    """
    BASIC_MAKER = float


class String(Descriptor):
    """
    This value must be a string, or be converted to one
    """
    BASIC_MAKER = str


class Regexp(String):
    """
    Base class for declaring regexp-based descriptors. Overload it's attribute REGEXP. Use as
    following:

    >>> class IPv6(Regexp):
    >>>     REGEXP = '(\A([0-9a-f]{1,4}:)' ...
    """
    REGEXP = r'.*'

    def __init__(self):
        super(Regexp, self).__init__()
        if isinstance(self.REGEXP, str):
            self.REGEXP = re.compile(self.REGEXP)

    def __call__(self, value: ConfigDictValue) -> str:
        value = super(Regexp, self).__call__(value)

        match = self.REGEXP.match(value)
        if not match:
            raise ConfigurationValidationError('value does not match %s' % (self.REGEXP.pattern,),
                                               value)

        return match.group(0)

    def __str__(self):
        return 'Regexp(%s)' % (self.REGEXP.pattern, )


class IPv4(Regexp):
    """
    This must be a valid IPv4 address (no hostnames allowed)
    """
    REGEXP = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'


class List(Descriptor):
    """
    This must be a list, made of entries of a descriptor (this is optional)
    """
    CHECKERS = [must_be_type(list, tuple)]
    BASIC_MAKER = list

    def __init__(self, type_desciptor: tp.Optional[Descriptor] = None):
        super().__init__()
        self.type_descriptor = type_desciptor or Descriptor()

    def __call__(self, value: ConfigDictValue) -> tp.List:
        value = super().__call__(value)

        return [self.type_descriptor(p) for p in value]

    def __str__(self):
        return 'List(%s)' % (self.type_descriptor, )


DictDescriptorKey = tp.NewType('DictDescriptorKey', Descriptor)


def create_key(descriptor: Descriptor, name: str, optional: bool = False,
               default: tp.Optional[tp.Any] = None) -> DictDescriptorKey:
    descriptor.name = name
    descriptor.optional = optional
    descriptor.default = default

    return descriptor


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
    BASIC_MAKER = dict
    CHECKERS = [must_be_type(dict)]

    UnknownKeyHandlerType = tp.Callable[[str, ConfigDictValue], tp.Any]

    def __init__(self, keys: tp.List[DictDescriptorKey],
                 unknown_key_mapper: UnknownKeyHandlerType = lambda str,
                                                                    data: data):
        super().__init__()
        self.keys = {item.name: item for item in keys}  # tp.Dict[str, DictDescriptorKey]
        self.unknown_key_mapper = unknown_key_mapper  # Dict.UnknownKeyHandlerType

    def __str__(self):
        return 'Dict(%s)' % (self.keys, )

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


class Union(Descriptor):
    """
    The type of one of the child descriptors. If posed as such:

    Union(List(), Dict())

    then value can be either a list or a dict
    """

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


BASE_LOOKUP_TABLE = {'int': Integer, 'float': Float, 'str': String, 'ipv4': IPv4, 'list': List,
                     'dict': Dict, 'any': Descriptor, 'bool': Boolean, 'union': Union}


def _get_descriptor_for(key: str, value: tp.Any) -> Descriptor:
    if value == '':
        return Descriptor()
    elif isinstance(value, str):
        if value in ('int', 'float', 'str', 'ipv4', 'any', 'bool'):
            return create_key(BASE_LOOKUP_TABLE[value](),
                              key, False, None)
    elif isinstance(value, dict):
        if 'type' not in value:
            return create_key(descriptor_from_dict(value),
                              key, False, None)
        else:
            args = ()
            type_ = value['type']
            if type_ == 'list':
                of = _get_descriptor_for('', value.get('of', ''))
                args = (of,)
            elif type_ == 'union':
                args = [_get_descriptor_for('', x) for x in value.get('of', [])]
            optional, default = False, None
            if 'default' in value:
                optional = True
                default = value['default']
            optional = value.get('optional', optional)
            descriptor = BASE_LOOKUP_TABLE[type_](*args)
            return create_key(descriptor, key, optional, default)
    elif isinstance(value, type):
        return _get_descriptor_for(key, value.__qualname__)
    else:
        raise ConfigurationSchemaError('invalid schema, unrecognized config object %s' % (value,))


def register_custom_descriptor(name: str):
    """
    A decorator used for registering custom descriptors in order to be loadable via
    descriptor_from_dict

    Use like:

    >>> @register_custom_descriptor('ipv6')
    >>> class IPv6(Regexp):
    >>>     REGEXP = '(\A([0-9a-f]{1,4}:)' ...

    :param name: under which it is supposed to be invokable
    """

    def inner(cls):
        BASE_LOOKUP_TABLE[name] = cls
        return cls

    return inner


def descriptor_from_dict(dct: dict) -> Descriptor:
    """
    Giving a Python dictionary-defined schema of the configuration, return a Descriptor-based one

    :param dct: something like
    {
        "a": "int",
        "b": "str",
        "c": {
            "type": "int"
            "optional": True,
            "default": 5
        },
        "d": {
            "a": "int",
            "b": "str"
        }
    }

    although you can pass "int", "float" and "str" without enclosing quotes, that will work too

    :return: a Descriptor-based schema
    """
    fields = []

    for key, value in dct.items():
        descriptor = _get_descriptor_for(key, value)
        fields.append(descriptor)

    return Dict(fields)
