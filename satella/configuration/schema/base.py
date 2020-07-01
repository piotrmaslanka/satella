import typing as tp

from satella.coding.concurrent import CallableGroup
from satella.exceptions import ConfigurationValidationError
from .registry import register_custom_descriptor

ConfigDictValue = tp.Optional[tp.Union[int, float, str, dict, list, bool]]
CheckerConditionType = tp.Callable[[ConfigDictValue], bool]
ObjectMakerType = tp.Callable[
    [ConfigDictValue], tp.Any]  # might raise ConfigurationSchemaError as well


class CheckerCondition:
    __slots__ = ('condition', 'description', 'is_pre_checker')

    PRE_CHECKER = 0
    POST_CHECKER = 1

    def __init__(self, condition: CheckerConditionType, description: str = u'',
                 is_pre_checker: bool = True):
        self.condition = condition
        self.description = description
        self.is_pre_checker = is_pre_checker

    def __call__(self, value):
        if not self.condition(value):
            raise ConfigurationValidationError(self.description, value)


def must_be_type(*cls_or_tuple):
    return CheckerCondition(condition=lambda v: isinstance(v, cls_or_tuple),
                            description='not one of types %s' % (cls_or_tuple,))


def must_be_one_of(*items):
    return CheckerCondition(condition=lambda v: v in items,
                            description='not in set %s' % (items,),
                            is_pre_checker=False)


@register_custom_descriptor('any')
class Descriptor:
    """
    Base class for a descriptor
    """
    __slots__ = ('pre_checkers', 'post_checkers', 'name', 'optional', 'default',
                 'my_exceptions')

    BASIC_MAKER = staticmethod(lambda v: v)
    MY_EXCEPTIONS = [TypeError, ValueError]  # a list of Exception classes
    CHECKERS = []  # a list of CheckerCondition

    def __init__(self):
        self.pre_checkers = CallableGroup()  # type: tp.Callable[[bool], None]
        self.post_checkers = CallableGroup()  # type: tp.Callable[[bool], None]
        self.name = None  # type: tp.Optional[str]
        self.optional = None  # type: tp.Optional[bool]
        self.default = None  # type: tp.Optional[tp.Any]

        for checker in self.__class__.CHECKERS:
            self.add_checker(checker)

        self.my_exceptions = tuple(self.MY_EXCEPTIONS)  # type: tp.Tuple[tp.Type[Exception], ...]

    def __str__(self):
        return '%s()' % (self.__class__.__qualname__,)

    def __call__(self, value: ConfigDictValue) -> tp.Any:
        """
        raises ConfigurationSchemaError: on invalid schema
        """
        self.pre_checkers(value)

        try:
            value = self.BASIC_MAKER(value)
        except self.my_exceptions as e:
            raise ConfigurationValidationError('could not pass to maker due to %s' % (e,), value)

        self.post_checkers(value)

        return value

    def add_checker(self, checker: CheckerCondition):
        if checker.is_pre_checker:
            self.pre_checkers.add(checker)
        else:
            self.post_checkers.add(checker)
