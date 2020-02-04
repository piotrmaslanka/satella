import logging
import typing as tp
import math
import time
import collections
import functools
from satella.coding import for_argument, precondition
from .base import LeafMetric, RUNTIME, DEBUG
logger = logging.getLogger(__name__)


# shamelessly taken from http://code.activestate.com/recipes/511478-finding-the-percentile-of-the-values/)
def percentile(n: tp.List[float], percent: float) -> float:
    """
    Find the percentile of a list of values.

    :param n: - is a list of values. Note this MUST BE already sorted.
    :param percent: - a float value from 0.0 to 1.0.

    :return: the percentile of the values
    """
    k = (len(n)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return n[int(k)]
    d0 = n[int(f)] * (c-k)
    d1 = n[int(c)] * (k-f)
    return d0+d1


class PercentileMetric(LeafMetric):
    """
    A metric that can register some values, sequentially, and then calculate percentiles from it

    :param last_calls: last calls to handle() to take into account
    :param percentiles: a sequence of percentiles to return in to_json
    """

    CLASS_NAME = 'percentile'

    def __init__(self, name, root_metric: 'Metric' = None, metric_level: str = None,
                 last_calls: int = 100, percentiles: tp.Sequence[float]=[0.5, 0.95]):
        super().__init__(name, root_metric, metric_level)
        self.last_calls = last_calls
        self.calls_queue = collections.deque()
        self.percentiles = percentiles

    def handle(self, level: int, time_taken: float) -> None:
        if self.can_process_this_level(level):
            if len(self.calls_queue) == self.last_calls:
                self.calls_queue.pop()
            self.calls_queue.appendleft(time_taken)

    def to_json(self) -> dict:
        output = []
        sorted_calls = sorted(self.calls_queue)
        for p_val in self.percentiles:
            if not sorted_calls:
                output.append({'percentile': p_val,
                               '_': 0.0})
            else:
                output.append({'percentile': p_val,
                               '_': percentile(sorted_calls, p_val)})
        return output

    @precondition(None, None, lambda x: x in (RUNTIME, DEBUG))
    def measure(self, include_exceptions: bool = True, logging_level: int = RUNTIME,
                value_getter: tp.Callable[[], float] = time.monotonic):
        """
        A decorator to measure a difference between some value after the method call
        and before it.

        By default, it will measure the execution time.

        Use like:

        >>> call_time = getMetric('root.metric_name.execution_time', 'percentile')
        >>> @call_time.measure()
        >>> def measure_my_execution(args):
        >>>     ...

        :param include_exceptions: whether to include exceptions
        :param logging_level: one of RUNTIME or DEBUG
        :param value_getter: a callable that takes no arguments and returns a float, which is
            the value
        """
        def outer(fun):
            @functools.wraps(fun)
            def inner(*args, **kwargs):
                start_value = value_getter()
                excepted = None
                try:
                    return fun(*args, **kwargs)
                except Exception as e:
                    excepted = e
                finally:
                    value_taken = value_getter() - start_value
                    if excepted is not None and not include_exceptions:
                        raise e

                    if logging_level == RUNTIME:
                        self.runtime(value_taken)
                    else:
                        self.debug(value_taken)

                    if e is not None:
                        raise e
            return inner
        return outer
