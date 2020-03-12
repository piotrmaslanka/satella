from abc import ABCMeta, abstractmethod
import typing as tp
import logging
import functools
import psutil

__all__ = ['GB', 'MB', 'KB', 'Any', 'All', 'GlobalAbsoluteValue', 'GlobalRelativeValue',
           'LocalRelativeValue', 'LocalAbsoluteValue', 'MemoryCondition', 'ZerothSeverity',
           'CustomCondition', 'Not']

logger = logging.getLogger(__name__)

GB = 1024*1024*1024
MB = 1024*1024
KB = 1024


class MemoryCondition(metaclass=ABCMeta):
    __slots__ = ('value', )

    def __init__(self, value: int):
        self.value = value

    @abstractmethod
    def can_fire(self, local_memory_data, local_maximum_consume: tp.Optional[int]) -> bool:
        """Has this severity level been reached?"""


class ZerothSeverity(MemoryCondition):
    def __init__(self):
        pass

    def can_fire(self, local_memory_data, local_maximum_consume: tp.Optional[int]) -> bool:
        return True


class OperationJoin(MemoryCondition):
    __slots__ = ('conditions', )

    def __init__(self, *conditions: MemoryCondition):
        self.conditions = conditions

    def can_fire(self, local_memory_data, local_maximum_consume: tp.Optional[int]) -> bool:
        return functools.reduce(self.OPERATOR, (
            condition.can_fire(local_memory_data, local_maximum_consume) for condition in
            self.conditions), self.STARTING_VALUE)


class Any(OperationJoin):
    """This is true if one of the arguments is True"""

    @staticmethod
    def OPERATOR(a, b):
        return a or b

    STARTING_VALUE = False


class All(OperationJoin):
    """This is true if all arguments are True"""

    @staticmethod
    def OPERATOR(a, b):
        return a and b

    STARTING_VALUE = True


class Not(MemoryCondition):
    """True only if provided condition is false"""
    __slots__ = ('condition', )

    def __int__(self, condition: MemoryCondition):
        self.condition = condition

    def can_fire(self, local_memory_data, local_maximum_consume: tp.Optional[int]) -> bool:
        return not self.condition.can_fire(local_memory_data, local_maximum_consume)


class GlobalAbsoluteValue(MemoryCondition):
    """If free memory globally falls below this many bytes, given severity level starts"""

    def can_fire(self, local_memory_data, local_maximum_consume: tp.Optional[int]) -> bool:
        return psutil.virtual_memory().available < self.value


class GlobalRelativeValue(MemoryCondition):
    """
    If percentage of global free memory falls below this many bytes, given severity level starts
    """

    def can_fire(self, local_memory_data, local_maximum_consume: tp.Optional[int]) -> bool:
        return psutil.virtual_memory().available / psutil.virtual_memory().total < (
                self.value / 100)


class LocalAbsoluteValue(MemoryCondition):
    """
    If free memory falls below this many bytes from what the program can maximally consume this
    severity level starts
    """

    def can_fire(self, local_memory_data, local_maximum_consume: tp.Optional[int]) -> bool:
        return local_maximum_consume - local_memory_data.rss < self.value


class LocalRelativeValue(MemoryCondition):
    """
    If percentage of memory available to this process in regards to what the program can
    maximally consume falls below this level, given severity level starts
    """

    def can_fire(self, local_memory_data, local_maximum_consume: tp.Optional[int]) -> bool:
        return local_memory_data.rss / local_maximum_consume < (1-self.value / 100)


class CustomCondition(MemoryCondition):
    """
    A custom condition. Condition that is true if attached callable/0 returns True.

    :param callable_: callable to call upon asking whether this condition is valid. This
        should be relatively cheap to compute.
    """
    __slots__ = ('callable', )

    def __init__(self, callable_: tp.Callable[[], bool]):
        self.callable = callable_

    def can_fire(self, local_memory_data, local_maximum_consume: tp.Optional[int]) -> bool:
        v = self.callable()
        logger.warning('Custom condition %s returning %s' % (self.callable, v))
        return v

