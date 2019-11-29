import copy
import typing as tp
import re

from satella.coding import rethrow_as, CallableGroup, for_argument
from ...exceptions import ConfigurationValidationError

__all__ = [
    'Descriptor',
    'Integer', 'Float', 'String',
    'IPv4',
    'List', 'Dict', 'create_key',
    'must_be_type',
    'must_be_one_of',
    'CheckerCondition',
    'ConfigDictValue',
]

ConfigDictValue = tp.Optional[tp.Union[int, float, str, dict, list, bool]]
CheckerConditionType = tp.Callable[[ConfigDictValue], bool]
ObjectMakerType = tp.Callable[
    [ConfigDictValue], tp.Any]  # might raise ConfigurationSchemaError as well

_NOP = lambda v: v


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
    BASIC_MAKER = _NOP  # of ObjectMakerType
    MY_EXCEPTIONS = [TypeError, ValueError] # a list of Exception classes
    CHECKERS = []   # a list of CheckerCondition

    def __init__(self):
        self.pre_checkers = CallableGroup()
        self.post_checkers = CallableGroup()

        for checker in self.__class__.CHECKERS:
            self.add_checker(checker)

    def convert(self, value: ConfigDictValue) -> tp.Any:
        """
        raises ConfigurationSchemaError: on invalid schema
        """
        self.pre_checkers(value)

        try:
            value = self.BASIC_MAKER(value)
        except cls.MY_EXCEPTIONS:
            raise ConfigurationValidationError('could not pass to maker', value)

        self.post_checkers(value)

        return value

    def add_checker(self, checker: CheckerCondition):
        if checker.is_pre_checker:
            self.pre_checkers.add(checker)
        else:
            self.post_checkers.add(checker)


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

    def convert(self, value: ConfigDictValue) -> str:
        value = super(Regexp, self).convert(value)

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

    def __init__(self, type_maker: ObjectMakerType = _NOP):
        super(List, self).__init__()
        self.type_maker = type_maker

    def convert(self, value: ConfigDictValue) -> tp.List:
        value = super(List, self).convert(value)

        return [self.type_maker(p) for p in value]


DictDescriptorKey = tp.NewType('DictDescriptorKey', Descriptor)


def create_key(descriptor: Descriptor, name: str, optional: bool = False,
               default=None) -> DictDescriptorKey:
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

    @for_argument('self', copy.copy)
    def convert(self, value: ConfigDictValue):
        assert isinstance(value, dict)
        value = super(Dict, self).convert(value)
        assert isinstance(value, dict)

        output = {}

        for key, keydescriptor in self.keys.items():
            try:
                v = value.pop(key)
            except KeyError:
                if keydescriptor.optional:
                    output[key] = keydescriptor.default
                else:
                    raise ConfigurationSchemaError('required key %s not found',
                                                   key)
            else:
                output[key] = keydescriptor.convert(v)

        for k, v in value.items():
            output[k] = self.unknown_key_mapper(k, v)

        return output
