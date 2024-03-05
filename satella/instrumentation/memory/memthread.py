from __future__ import annotations
import logging
import os
import typing as tp
import weakref

import psutil

from satella.coding.concurrent import CallableGroup, CallNoOftenThan, CancellableCallback, \
    IntervalTerminableThread
from satella.coding.structures import Singleton
from .conditions import BaseCondition, ZerothSeverity

logger = logging.getLogger(__name__)

__all__ = ['MemoryPressureManager']


@Singleton
class MemoryPressureManager(IntervalTerminableThread):
    """
    Manager of the memory pressure.

    The program is in some severity state. The baseline state is 0, meaning everything's OK.

    Please note that it is sufficient to instantiate this class for the thread to run.

    Eg.

    >>> mt = MemoryPressureManager(maximum_available=4*GB, severity_levels=[GlobalRelativeValue(20),
    >>>                            GlobalRelativeValue(10)])
    >>> @mt.register_on_severity(1)
    >>> def trigger_a():
    >>>     print('80% consumption of memory exceeded')
    >>> @mt.register_on_severity(2)
    >>> def trigger_b():
    >>>     print('90% consumption of memory exceeded')

    As well, this object is a singleton.

    :param maximum_available: maximum amount of memory that this program can use
    :param severity_levels: this defines the levels of severity. A level is reached when program's
        consumption is other this many percent of it's maximum_available amount of memory. Note that you need to
        specify only the abnormal memory levels, the default level of 0 will be added automatically.
    :param check_interval: amount of seconds of pause between consecutive checks, or
        a time string
    :param log_transitions: whether to log to logger when a transition takes place

    :ivar severity_level: current severity level (int)
        0 means memory is OK, 1 and more means memory is progressively more limited
    """

    def __init__(self, maximum_available: tp.Optional[int] = None,
                 severity_levels: tp.List[BaseCondition] = None,
                 check_interval: tp.Union[str, int] = 10,
                 log_transitions: bool = True):
        super().__init__(check_interval, name='memory pressure manager', daemon=True)
        self.log_transitions = log_transitions  # type: bool
        self.process = psutil.Process(os.getpid())  # type: psutil.Process
        self.maximum_available = maximum_available  # type: int
        self.severity_levels = [ZerothSeverity()] + (
                severity_levels or [])  # type: tp.List[BaseCondition]

        self.callbacks_on_entered = [CallableGroup(gather=False) for _ in
                                     range(len(
                                         self.severity_levels))]  # type: tp.List[CallableGroup]
        self.callbacks_on_remains = [CallableGroup(gather=False) for _ in
                                     range(len(
                                         self.severity_levels))]  # type: tp.List[CallableGroup]
        self.callbacks_on_left = [CallableGroup(gather=False) for _ in
                                  range(len(
                                      self.severity_levels))]  # type: tp.List[CallableGroup]
        self.objects_to_cleanup_on_entered = [[] for _ in range(len(self.severity_levels))]
        self.callbacks_on_memory_normal = CallableGroup(gather=False)
        self.severity_level = 0  # type: int
        self.stopped = False  # type: bool
        self.start()

    @staticmethod
    def cleanup_on_entered(target_level: int, obj: tp.Any,
                           collector: tp.Callable[[tp.Any], None] = lambda y: y.cleanup()):
        """
        Attempt to recover memory by calling a particular method on an object.

        A weak reference will be stored to this object

        :param target_level: cleanup will be attempted on entering this severity level
        :param obj: object to call this on
        :param collector: a lambda to call a routine on this object
        """
        MemoryPressureManager().objects_to_cleanup_on_entered[target_level].append((weakref.ref(obj), collector))

    def advance_to_severity_level(self, target_level: int):
        while self.severity_level != target_level:
            delta = target_level - self.severity_level
            delta = int(delta / abs(delta))

            if delta > 0:
                # Means we are ENTERING a severity level
                self.severity_level += delta
                self.callbacks_on_entered[self.severity_level]()
                new_list = []
                for ref, collector in self.objects_to_cleanup_on_entered[self.severity_level]:
                    obj = ref()
                    if obj is not None:
                        collector(obj)
                        new_list.append((ref, collector))
                self.objects_to_cleanup_on_entered[self.severity_level] = new_list
                if self.log_transitions:
                    logger.warning('Entered severity level %s' % (self.severity_level,))
            elif delta < 0:
                # Means we are LEAVING a severity level
                self.callbacks_on_left[self.severity_level]()
                if self.log_transitions:
                    logger.warning('Left severity level %s' % (self.severity_level,))
                self.severity_level += delta
                if self.severity_level == 0:
                    self.callbacks_on_memory_normal()

    def stop(self):
        """Stop this thread from operating"""
        self.stopped = True

    def resume(self):
        """Resume the operation of this thread"""
        self.stopped = False

    def loop(self) -> None:
        if self.stopped:
            return

        self.callbacks_on_memory_normal.remove_cancelled()

        for cg in self.callbacks_on_entered:
            cg.remove_cancelled()

        for cg in self.callbacks_on_left:
            cg.remove_cancelled()

        for cg in self.callbacks_on_remains:
            cg.remove_cancelled()

        severity_level = self.calculate_severity_level()
        if self.severity_level != severity_level:
            self.advance_to_severity_level(severity_level)
        else:
            self.callbacks_on_remains[severity_level]()

    def calculate_severity_level(self) -> int:
        """
        This returns a severity level. 0 is the baseline severity level.
        """
        memory_info = self.process.memory_info()
        for level, condition in reversed(list(enumerate(self.severity_levels))):
            if condition.can_fire(memory_info, self.maximum_available):
                return level

    @staticmethod
    def register_on_memory_normal(fun: tp.Callable) -> CancellableCallback:
        """
        Register this handler to fire when memory state falls back to 0.

        This will be fired once, once memory state falls back to normal.

        :param fun: callable to register
        :return: a CancellableCallback under this callback is registered
        """
        cc = CancellableCallback(fun)
        MemoryPressureManager().callbacks_on_memory_normal.add(cc)
        return cc

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
            cc = CancellableCallback(fun)
            MemoryPressureManager().callbacks_on_entered[severity].add(cc)
            return cc

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
            cc = CancellableCallback(fun)
            MemoryPressureManager().callbacks_on_left[severity].add(cc)
            return cc

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
            cno = CallNoOftenThan(call_no_more_often_than, fun)
            cc = CancellableCallback(cno)
            MemoryPressureManager().callbacks_on_remains[severity].add(cc)
            return cc

        return outer
