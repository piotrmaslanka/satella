import copy
import inspect
import time
import typing as tp
from concurrent.futures import Future
from functools import wraps     # import from functools to prevent circular import exception

__all__ = ['measure', 'time_as_int', 'time_ms', 'sleep', 'time_us']


def sleep(x: float, abort_on_interrupt: bool = False) -> bool:
    """
    Sleep for given interval.

    This won't be interrupted by KeyboardInterrupted, and always will sleep for given time interval.
    This will return at once if x is negative

    :param x: the interval to wait
    :param abort_on_interrupt: whether to abort at once when KeyboardInterrupt is seen
    :returns: whether the function has completed its sleep naturally. False is seen on
        aborts thanks to KeyboardInterrupt only if abort_on_interrupt is True
    """
    if x < 0:
        return

    with measure() as measurement:
        while measurement() < x:
            try:
                time.sleep(x - measurement())
            except KeyboardInterrupt:
                if abort_on_interrupt:
                    return False
                pass
    return True


def time_as_int() -> int:
    """
    Syntactic sugar for

    >>> from time import time
    >>> int(time())
    """
    return int(time.time())


def time_ms() -> int:
    """
    Syntactic sugar for

    >>> from time import time
    >>> int(time()*1000)

    This will try to use time.time_ns() if available
    """
    try:
        return time.time_ns() // 1000000
    except AttributeError:
        return int(time.time() * 1000)


def time_us() -> int:
    """
    Syntactic sugar for

    >>> from time import time
    >>> int(time()*1000000)

    This will try to use time.time_ns() if available
    """
    try:
        return time.time_ns() // 1000
    except AttributeError:
        return int(time.time() * 1000000)


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

    This will also correctly work on methods, correctly inserting the measurement object after
    self/cls:

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

    Note that if you're using the decorator form, this object will be first copied and then
    passed to the function/future. This is to prevent undefined behaviour during multithreading.
    Also, the timer that you pass to this function will be started/not started, depending on what
    you set earlier. .reset() will be called on a copy of this object.

    :param stop_on_stop: stop elapsing time upon calling .stop()/exiting the context manager.
        If this is set to False then .start() and .stop() won't work and calling them will raise a
        TypeError.
    :param adjust: interval to add to current time upon initialization
    :param time_getter_callable: callable/0 -> float to get the time with
    :param create_stopped: if this is set to True, you will manually need to call .start()
    """
    __slots__ = ('started_on', 'elapsed', 'stopped_on', 'stop_on_stop', 'time_getter_callable',
                 'create_stopped')

    def __init__(self, future_to_measure: tp.Optional[Future] = None, stop_on_stop: bool = True,
                 adjust: float = 0.0, time_getter_callable: tp.Callable[[], float] = time.monotonic,
                 create_stopped: bool = False):
        self.time_getter_callable = time_getter_callable
        self.started_on = time_getter_callable() + adjust
        self.create_stopped = create_stopped
        if create_stopped:
            self.elapsed = 0
            self.stopped_on = self.started_on
        else:
            self.elapsed = None
            self.stopped_on = None
        self.stop_on_stop = stop_on_stop
        if future_to_measure is not None:
            future_to_measure.add_done_callback(lambda fut: self.stop())

    def reset_and_start(self):
        """
        Syntactic sugar for calling reset() and then start()
        """
        self.reset()
        self.start()

    def has_exceeded(self, value: float) -> bool:
        """
        Return whether the timer has exceeded provided value
        """
        return self() > value

    def raise_if_exceeded(self, value: float, exc_class: tp.Type[Exception] = TimeoutError):
        """
        Raise provided exception, with no arguments, if timer has clocked more than provided value.

        If no exc_class is provided, TimeoutError will be raised by default.
        """
        if self.has_exceeded(value):
            raise exc_class()

    def reset(self):
        """
        Reset the counter, enabling it to start counting after a .stop() call.
        This will put the counter in a STOPPED mode if it's running already.
        """
        self.stopped_on = self.started_on = self.time_getter_callable()
        self.elapsed = 0

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
                if inspect.isgeneratorfunction(func):
                    @wraps(func)
                    def inner(*args, **kwargs):
                        s = copy.copy(self)
                        if not s.create_stopped:
                            s.reset()
                            with s:
                                yield from func(s, *args, **kwargs)
                        else:
                            yield from func(s, *args, **kwargs)

                    return inner
                else:
                    @wraps(func)
                    def inner(*args, **kwargs):
                        s = copy.copy(self)
                        if not s.create_stopped:
                            s.reset()
                            with s:
                                return func(s, *args, **kwargs)
                        else:
                            return func(s, *args, **kwargs)

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
