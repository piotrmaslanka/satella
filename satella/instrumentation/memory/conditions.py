from abc import ABCMeta, abstractmethod
import typing as tp
import functools
import psutil

__all__ = ['GB', 'MB', 'KB', 'Any', 'All', 'GlobalAbsoluteValue', 'GlobalRelativeValue',
           'LocalRelativeValue', 'LocalAbsoluteValue', 'BaseCondition', 'ZerothSeverity',
           'CustomCondition', 'Not']

GB = 1024*1024*1024
MB = 1024*1024
KB = 1024


class BaseCondition(metaclass=ABCMeta):
    __slots__ = ()

    @abstractmethod
    def can_fire(self, local_memory_data, local_maximum_consume: tp.Optional[int]) -> bool:
        """Has this severity level been reached?"""


class MemoryCondition(BaseCondition, metaclass=ABCMeta):
    __slots__ = ('value', )

    def __init__(self, value: int):
        self.value = value


class ZerothSeverity(BaseCondition):
    __slots__ = ()

    def can_fire(self, local_memory_data, local_maximum_consume: tp.Optional[int]) -> bool:
        return True


class OperationJoin(BaseCondition):
    __slots__ = ('conditions', )

    def __init__(self, *conditions: BaseCondition):
        self.conditions = conditions

    def can_fire(self, local_memory_data, local_maximum_consume: tp.Optional[int]) -> bool:
        return functools.reduce(self.OPERATOR, (
            condition.can_fire(local_memory_data, local_maximum_consume) for condition in
            self.conditions), self.STARTING_VALUE)


class Any(OperationJoin):
    """This is true if one of the arguments is True"""
    __slots__ = ()

    @staticmethod
    def OPERATOR(a, b):
        return a or b

    STARTING_VALUE = False


class All(OperationJoin):
    """This is true if all arguments are True"""
    __slots__ = ()

    @staticmethod
    def OPERATOR(a, b):
        return a and b

    STARTING_VALUE = True


class Not(BaseCondition):
    """True only if provided condition is false"""
    __slots__ = ('condition', )

    def __init__(self, condition: BaseCondition):
        self.condition = condition

    def can_fire(self, local_memory_data, local_maximum_consume: tp.Optional[int]) -> bool:
        return not self.condition.can_fire(local_memory_data, local_maximum_consume)


class GlobalAbsoluteValue(MemoryCondition):
    """If free memory globally falls below this many bytes, given severity level starts"""
    __slots__ = ()

    def can_fire(self, local_memory_data, local_maximum_consume: tp.Optional[int]) -> bool:
        return psutil.virtual_memory().available < self.value


class GlobalRelativeValue(MemoryCondition):
    """
    If percentage of global free memory falls below this many bytes, given severity level starts
    """
    __slots__ = ()

    def can_fire(self, local_memory_data, local_maximum_consume: tp.Optional[int]) -> bool:
        return psutil.virtual_memory().available / psutil.virtual_memory().total < (
                self.value / 100)


class LocalAbsoluteValue(MemoryCondition):
    """
    If free memory falls below this many bytes from what the program can maximally consume this
    severity level starts
    """
    __slots__ = ()

    def can_fire(self, local_memory_data, local_maximum_consume: tp.Optional[int]) -> bool:
        return local_maximum_consume - local_memory_data.rss < self.value


class LocalRelativeValue(MemoryCondition):
    """
    If percentage of memory available to this process in regards to what the program can
    maximally consume falls below this level, given severity level starts
    """
    __slots__ = ()

    def can_fire(self, local_memory_data, local_maximum_consume: tp.Optional[int]) -> bool:
        return local_memory_data.rss / local_maximum_consume < (1-self.value / 100)


class CustomCondition(BaseCondition):
    """
    A custom condition. Condition that is true if attached callable/0 returns True.

    :param callable_: callable to call upon asking whether this condition is valid. This
        should be relatively cheap to compute.
    """
    __slots__ = ('callable', )

    def __init__(self, callable_: tp.Callable[[], bool]):
        self.callable = callable_

    def can_fire(self, local_memory_data, local_maximum_consume: tp.Optional[int]) -> bool:
        return self.callable()

