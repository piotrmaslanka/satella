import logging
import os
import time
import typing as tp

import psutil

from satella.coding.concurrent import CallableGroup, CallNoOftenThan
from satella.coding.concurrent import TerminableThread
from satella.coding.structures import Singleton
from satella.time import measure
from .conditions import BaseCondition, ZerothSeverity

logger = logging.getLogger(__name__)

__all__ = ['MemoryPressureManager']


@Singleton
class MemoryPressureManager(TerminableThread):
    """
    Manager of the memory pressure.

    The program is in some severity state. The baseline state is 0, meaning everything's OK.

    Please note that it is sufficient to instantiate this class for the thread to run.

    Eg.

    >>> mt = MemoryPressureManager(maximum_available=4*GB, severity_levels=[80, 90])
    >>> @mt.register_on_severity(1)
    >>> def trigger_a():
    >>>     print('80% consumption of memory exceeded')
    >>> @mt.register_on_severity(2)
    >>> def trigger_b():
    >>>     print('90% consumption of memory exceeded')

    :param maximum_available: maximum amount of memory that this program can use
    :param severity_levels: this defines the levels of severity. A level is reached when program's
        consumption is other this many percent of it's maximum_available amount of memory.
    :param check_interval: amount of seconds of pause between consecutive checks
    :param log_transitions: whether to log to logger when a transition takes place
    """

    def __init__(self, maximum_available: tp.Optional[int] = None,
                 severity_levels: tp.List[BaseCondition] = None,
                 check_interval: int = 10,
                 log_transitions: bool = True):
        super().__init__(daemon=True)
        self.log_transitions = log_transitions          # type: bool
        self.process = psutil.Process(os.getpid())      # type: psutil.Process
        self.maximum_available = maximum_available      # type: int
        self.severity_levels = [ZerothSeverity()] + (
                severity_levels or [])                  # type: tp.List[BaseCondition]

        self.callbacks_on_entered = [CallableGroup(gather=False) for _ in
                                     range(len(
                                         self.severity_levels))]  # type: tp.List[CallableGroup]
        self.callbacks_on_remains = [CallableGroup(gather=False) for _ in
                                     range(len(
                                         self.severity_levels))]  # type: tp.List[CallableGroup]
        self.callbacks_on_left = [CallableGroup(gather=False) for _ in
                                  range(len(
                                      self.severity_levels))]  # type: tp.List[CallableGroup]
        self.current_severity_level = 0             # type: int
        self.stopped = False                        # type: bool
        self.check_interval = check_interval        # type: int
        self.start()

    def advance_to_severity_level(self, target_level: int):
        while self.current_severity_level != target_level:
            delta = target_level - self.current_severity_level
            delta = int(delta / abs(delta))

            if delta > 0:
                # Means we are ENTERING a severity level
                self.current_severity_level += delta
                self.callbacks_on_entered[self.current_severity_level]()
                if self.log_transitions:
                    logger.warning('Entered severity level %s' % (self.current_severity_level, ))
            elif delta < 0:
                # Means we are LEAVING a severity level
                self.callbacks_on_left[self.current_severity_level]()
                if self.log_transitions:
                    logger.warning('Left severity level %s' % (self.current_severity_level, ))
                self.current_severity_level += delta

    def stop(self):
        """Stop this thread from operating"""
        self.stopped = True

    def resume(self):
        """Resume the operation of this thread"""
        self.stopped = False

    def loop(self) -> None:
        if self.stopped:
            return time.sleep(self.check_interval)

        with measure() as measurement:
            severity_level = self.calculate_severity_level()
            if self.current_severity_level != severity_level:
                self.advance_to_severity_level(severity_level)
            else:
                self.callbacks_on_remains[severity_level]()

        elapsed = measurement()
        if elapsed < self.check_interval:
            time.sleep(self.check_interval - elapsed)

    def calculate_severity_level(self) -> int:
        """
        This returns a severity level. 0 is the baseline severity level.
        """
        memory_info = self.process.memory_info()
        for level, condition in reversed(list(enumerate(self.severity_levels))):
            if condition.can_fire(memory_info, self.maximum_available):
                return level

    @staticmethod
    def register_on_entered_severity(severity: int):
        """
        Register this handler to fire on entered a particular severity level.

        This means that situation has gotten worse.

        Use like this:

        >>> MemoryPressureManager.register_on_entered_severity(1)
        >>> def entered_severity_one():
        >>>     print('Entered memory severity level 1')

        :param severity: severity level to react to
        """

        def outer(fun):
            MemoryPressureManager().callbacks_on_entered[severity].add(fun)
            return fun

        return outer

    @staticmethod
    def register_on_left_severity(severity: int):
        """
        Register a handler to be called when given severity level is left. This means
        that we have advanced to a lower severity level.

        >>> MemoryPressureManager.register_on_left_severity(1)
        >>> def entered_severity_one():
        >>>     print('Memory comsumption no longer 1')


        :param severity: severity level to leave
        """
        def outer(fun):
            MemoryPressureManager().callbacks_on_left[severity].add(fun)
            return fun
        return outer

    @staticmethod
    def register_on_remaining_in_severity(severity: int, call_no_more_often_than: int = 0):
        """
        Register this handler to fire on remaining in a particular severity level. Use like this:

        >>> MemoryPressureManager.register_on_remaining_in_severity(0, 30)
        >>> def entered_severity_one():
        >>>     print('Memory comsumption OK. I am called no more often than each 30 seconds')

        :param severity: severity level
        :param call_no_more_often_than: call no more often than this amount of seconds
        """

        def outer(fun):
            MemoryPressureManager().callbacks_on_remains[severity].add(
                CallNoOftenThan(call_no_more_often_than, fun))
            return fun

        return outer
