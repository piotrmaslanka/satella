import typing as tp
import time
from concurrent.futures import Future

from functools import wraps

__all__ = ['measure']


class measure:
    """
    A class used to measure time elapsed. Use for example like this:

    >>> with measure() as measurement:
    >>>     time.sleep(1)
    >>>     print('This has taken so far', measurement(), 'seconds')
    >>>     time.sleep(1)
    >>> print('A total of ', measurement(), 'seconds have elapsed')

    You can also use the .start() method instead of context manager. Time measurement
    will stop after exiting or calling .stop() depending on stop_on_stop flag.

    Time elapsing starts after the counter is created. If you wish to start it manually,
    please specify create_stopped=True

    When instantiated and called with no arguments, this will return the time elapsed:

    >>> a = measure()
    >>> time.sleep(0.5)
    >>> assert a() >= 0.5

    You can also decorate your functions to have them keep track time of their execution, like that:

    >>> @measure()
    >>> def measuring(measurement_object: measure, *args, **kwargs):
    >>>     ...

    This will also correctly work on methods, correctly inserting the measurement object after self/cls:

    >>> class Test:
    >>>     @measure()
    >>>     def measuring(self, measurement_object: measure):
    >>>         ...

    You can also measure how long does executing a future take, eg.

    >>> future = get_my_future()
    >>> measurement = measure(future)
    >>> future.result()
    >>> print('Executing the future took', measurement(), 'seconds')

    In case a future is passed, the measurement will stop automatically as soon as the future
    returns with a result (or exception).

    Note that in order to reuse a single counter you must .reset() it first. Just calling .start()
    after .stop() will result in the timer being resumed instead!

    :param stop_on_stop: stop elapsing time upon calling .stop()/exiting the context manager.
        If this is set to False then .start() and .stop() won't work and calling them will raise a
        TypeError.
    :param adjust: interval to add to current time upon initialization
    :param time_getter_callable: callable/0 -> float to get the time with
    :param create_stopped: if this is set to True, you will manually need to call .start()
    """
    __slots__ = ('started_on', 'elapsed', 'stopped_on', 'stop_on_stop', 'time_getter_callable')

    def __init__(self, future_to_measure: tp.Optional[Future] = None, stop_on_stop: bool = True,
                 adjust: float = 0.0, time_getter_callable: tp.Callable[[], float] = time.monotonic,
                 create_stopped: bool = False):
        self.time_getter_callable = time_getter_callable
        self.started_on = time_getter_callable() + adjust
        if create_stopped:
            self.elapsed = 0
            self.stopped_on = self.started_on
        else:
            self.elapsed = None
            self.stopped_on = None
        self.stop_on_stop = stop_on_stop
        if future_to_measure is not None:
            future_to_measure.add_done_callback(lambda fut: self.stop())


    def reset(self):
        """
        Reset the counter, enabling it to start counting after a .stop() call

        :raise TypeError: the counter is not stopped
        """
        if self.stopped_on is None:
            raise TypeError('The counter has not been stopped')
        self.started_on = self.time_getter_callable()
        self.elapsed = None
        self.stopped_on = None

    def start(self) -> None:
        """Start measuring time or resume measuring it"""
        if not self.stop_on_stop:
            raise TypeError('stop_on_stop is disabled for this counter!')
        if self.stopped_on is None:
            raise TypeError('the counter is already running!')

        if self.stopped_on is not None:
            self.started_on = self.time_getter_callable() - self.elapsed
            self.stopped_on = None
        self.started_on = self.time_getter_callable()
        self.elapsed = None

    def update(self) -> None:
        """Alias for .start()"""
        self.start()

    def adjust(self, interval: float) -> None:
        """Add given value to internal started_at counter"""
        self.started_on += interval

    def __call__(self, fun: tp.Optional[tp.Callable] = None) -> float:
        if fun is None:
            if self.stop_on_stop and self.elapsed is not None:
                return self.elapsed
            return self.time_getter_callable() - self.started_on
        else:
            from satella.coding.decorators import auto_adapt_to_methods

            @auto_adapt_to_methods
            def outer(func):
                @wraps(func)
                def inner(*args, **kwargs):
                    with self:
                        return func(self, *args, **kwargs)
                return inner
            return outer(fun)

    def __enter__(self):
        if self.elapsed is not None and self.stop_on_stop:
            self.start()
        return self

    def stop(self) -> None:
        """
        Stop counting time

        :raises TypeError: stop_on_stop is enabled or the counter has already been stopped
        """
        if not self.stop_on_stop:
            raise TypeError('stop_on_stop is disabled for this counter!')
        if self.stopped_on is not None:
            raise TypeError('counter already stopped!')

        self.stopped_on = self.time_getter_callable()
        self.elapsed = self.stopped_on - self.started_on

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.stop_on_stop:
            self.stop()
        return False
