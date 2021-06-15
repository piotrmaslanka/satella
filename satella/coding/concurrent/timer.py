import typing as tp
import logging
import threading
import time

from satella.coding.recast_exceptions import log_exceptions
from .monitor import Monitor
from ..structures.heaps.time import TimeBasedHeap
from ..structures.singleton import Singleton
from ...time.parse import parse_time_string

logger = logging.getLogger(__name__)


class Timer:
    """
    A copy of threading.Timer but all objects are backed and waited upon in a single thread.
    They can be executed either in background monitor's thread or a separate thread can be
    spawned for them.

    There might be up to a second of delay before the timer is picked up.

    If spawn_separate is False, exceptions will be logged

    :param interval: amount of seconds that should elapsed between calling start() and function
        executing. Can be also a time string.
    :param function: function to execute
    :param args: argument for function
    :param kwargs: kwargs for function
    :param spawn_separate: whether to call the function in a separate thread
    """
    __slots__ = ('args', 'kwargs', 'spawn_separate', 'interval',
                 'function', 'execute_at', 'cancelled')

    def __init__(self, interval: tp.Union[str, float], function, args=None, kwargs=None,
                 spawn_separate=False):
        self.args = args or []
        self.kwargs = kwargs or {}
        self.spawn_separate = spawn_separate
        self.interval = parse_time_string(interval)
        self.function = function
        self.execute_at = None
        self.cancelled = False

    def start(self) -> None:
        """
        Order this timer task to be executed in interval seconds
        """
        execute_at = time.monotonic() + self.interval
        tbt = TimerBackgroundThread()
        with Monitor.acquire(tbt):
            tbt.timer_objects.put(execute_at, self)

    def cancel(self) -> None:
        """Do not execute this timer"""
        self.cancelled = True

    def _try_execute(self):
        if self.cancelled:
            return
        if self.spawn_separate:
            threading.Thread(target=self.function, args=self.args, kwargs=self.kwargs,
                             daemon=True).start()
        else:
            self.function(*self.args, **self.kwargs)


@Singleton
class TimerBackgroundThread(threading.Thread, Monitor):
    def __init__(self):
        super().__init__(name='timer background thread', daemon=True)
        Monitor.__init__(self)
        self.timer_objects = TimeBasedHeap()  # type: TimeBasedHeap[Timer]
        self.start()

    def run(self):
        while True:
            try:
                ts, _ = self.timer_objects.peek_closest()
                delay = min(ts - time.monotonic(), 1)
                if delay < 0:
                    delay = 0
            except IndexError:
                delay = 1
            time.sleep(delay)
            with Monitor.acquire(self):
                items_to_exec = self.timer_objects.pop_less_than(time.monotonic())

            for item in items_to_exec:
                with log_exceptions(logger, swallow_exception=True):
                    item[1]._try_execute()
