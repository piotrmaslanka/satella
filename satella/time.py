import logging
import typing as tp
import time
import functools

logger = logging.getLogger(__name__)

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

    You can also decorate your functions to have them keep track time of their execution, like that:

    >>> @measure()
    >>> def measuring(measurement_object: measure, *args, **kwargs):
    >>>     ...

    :param stop_on_stop: stop elapsing time upon calling .stop()/exiting the context manager
    :param adjust: interval to add to current time upon initialization
    """
    def __init__(self, stop_on_stop: bool = True, adjust: float = 0.0):
        self.started_on = time.monotonic() + adjust
        self.elapsed = None
        self.stopped_on = None
        self.stop_on_stop = stop_on_stop

    def start(self) -> None:
        """Start measuring time or update the internal counter"""
        self.started_on = time.monotonic()

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
            return time.monotonic() - self.started_on
        else:
            @functools.wraps(fun)
            def inner(*args, **kwargs):
                with self:
                    return fun(self, *args, **kwargs)
            return inner

    def __enter__(self):
        self.start()
        return self

    def stop(self) -> None:
        """Stop counting time"""
        self.stopped_on = time.monotonic()
        self.elapsed = self.stopped_on - self.started_on

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False
