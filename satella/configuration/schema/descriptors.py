import copy
import typing as tp
import re

from satella.coding import rethrow_as, CallableGroup, for_argument
from ...exceptions import ConfigurationValidationError, ConfigurationSchemaError

__all__ = [
    'Descriptor',
    'Integer', 'Float', 'String', 'Boolean',
    'IPv4',
    'List', 'Dict', 'create_key',
    'must_be_type',
    'must_be_one_of',
    'CheckerCondition',
    'ConfigDictValue',
    'descriptor_from_dict',
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
    BASIC_MAKER = staticmethod(lambda v: v)
    MY_EXCEPTIONS = [TypeError, ValueError] # a list of Exception classes
    CHECKERS = []   # a list of CheckerCondition

    def __init__(self):
        self.pre_checkers = CallableGroup()
        self.post_checkers = CallableGroup()
        self.name = None
        self.optional = None
        self.default = None

        for checker in self.__class__.CHECKERS:
            self.add_checker(checker)

    def __call__(self, value: ConfigDictValue) -> tp.Any:
        """
        raises ConfigurationSchemaError: on invalid schema
        """
        self.pre_checkers(value)

        try:
            value = self.BASIC_MAKER(value)
        except self.MY_EXCEPTIONS:
            raise ConfigurationValidationError('could not pass to maker', value)

        self.post_checkers(value)

        return value

    def add_checker(self, checker: CheckerCondition):
        if checker.is_pre_checker:
            self.pre_checkers.add(checker)
        else:
            self.post_checkers.add(checker)


@staticmethod
def _make_boolean(v: tp.Any) -> bool:
    if isinstance(v, str):
        if v.upper() == 'TRUE':
            return True
        elif v.upper() == 'FALSE':
            return False
        else:
            raise ConfigurationValidationError('Unknown value of "%s" posing to be a bool' % (v, ))
    else:
        return bool(v)


class Boolean(Descriptor):
    BASIC_MAKER = _make_boolean


class Integer(Descriptor):
    BASIC_MAKER = int


class Float(Descriptor):
    BASIC_MAKER = float


class String(Descriptor):
    BASIC_MAKER = str


class Regexp(String):
    REGEXP = r'.*'

    def __init__(self):
        super(Regexp, self).__init__()
        if isinstance(self.REGEXP, str):
            self.REGEXP = re.compile(self.REGEXP)

    def __call__(self, value: ConfigDictValue) -> str:
        value = super(Regexp, self).__call__(value)

        match = self.REGEXP.match(value)
        if not match:
            raise ConfigurationValidationError('value does not match %s' % (self.REGEXP.pattern, ), value)

        return match.group(0)


class IPv4(Regexp):
    REGEXP = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'


class List(Descriptor):
    CHECKERS = [must_be_type(list, tuple)]
    BASIC_MAKER = list
    MY_EXCEPTIONS = []

    def __init__(self, type_desciptor: tp.Optional[Descriptor] = None):
        super(List, self).__init__()
        self.type_descriptor = type_desciptor or Descriptor()

    def __call__(self, value: ConfigDictValue) -> tp.List:
        value = super(List, self).__call__(value)

        return [self.type_descriptor(p) for p in value]


DictDescriptorKey = tp.NewType('DictDescriptorKey', Descriptor)


def create_key(descriptor: Descriptor, name: str, optional: bool = False,
               default: tp.Optional[tp.Any] = None) -> DictDescriptorKey:
    descriptor.name = name
    descriptor.optional = optional
    descriptor.default = default

    return descriptor


class Dict(Descriptor):
    BASIC_MAKER = dict
    MY_EXCEPTIONS = []
    CHECKERS = [must_be_type(dict)]

    UnknownKeyHandlerType = tp.Callable[[str, ConfigDictValue], tp.Any]

    def __init__(self, keys: tp.List[DictDescriptorKey],
                 unknown_key_mapper: UnknownKeyHandlerType = lambda str,
                                                                    data: data):
        super(Dict, self).__init__()
        self.keys = {item.name: item for item in keys}  #  tp.Dict[str, DictDescriptorKey]
        self.unknown_key_mapper = unknown_key_mapper    # Dict.UnknownKeyHandlerType

    def __call__(self, value: ConfigDictValue) -> dict:
        value = copy.copy(value)
        assert isinstance(value, dict), 'value is an instance of %s' % (repr(value), )
        value = super(Dict, self).__call__(value)
        assert isinstance(value, dict), 'value is an instance of %s' % (repr(value), )

        output = {}

        for key, key_descriptor in self.keys.items():
            try:
                v = value.pop(key)
            except KeyError:
                if key_descriptor.optional:
                    output[key] = key_descriptor.default
                else:
                    raise ConfigurationValidationError('required key %s not found' % (key, ))
            else:
                output[key] = key_descriptor(v)

        for k, v in value.items():
            output[k] = self.unknown_key_mapper(k, v)

        return output


BASE_LOOKUP_TABLE = {'int': Integer, 'float': Float, 'str': String, 'ipv4': IPv4, 'list': List, 'dict': Dict,
                     'any': Descriptor, 'bool': Boolean}


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
            type = value['type']
            if type == 'list':
                of = _get_descriptor_for('', value.get('of', ''))
                args = (of, )
            optional, default = False, None
            if 'default' in value:
                optional = True
                default = value['default']
            optional = value.get('optional', optional)
            descriptor = BASE_LOOKUP_TABLE[type](*args)
            return create_key(descriptor, key, optional, default)
    else:
        raise ConfigurationSchemaError('invalid schema, unrecognized config object %s' % (value, ))


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
    :return: a Descriptor-based schema
    """
    fields = []

    for key, value in dct.items():
        descriptor = _get_descriptor_for(key, value)
        fields.append(descriptor)

    return Dict(fields)
