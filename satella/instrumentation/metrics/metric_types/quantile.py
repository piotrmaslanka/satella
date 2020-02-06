import collections
import functools
import inspect
import logging
import time
import typing as tp

import math

from .base import EmbeddedSubmetrics, RUNTIME, LeafMetric
from .registry import register_metric

logger = logging.getLogger(__name__)


# shamelessly taken from http://code.activestate.com/recipes/511478-finding-the-percentile-of-the-values/)
def percentile(n: tp.List[float], percent: float) -> float:
    """
    Find the percentile of a list of values.

    :param n: - is a list of values. Note this MUST BE already sorted.
    :param percent: - a float value from 0.0 to 1.0.

    :return: the percentile of the values
    """
    k = (len(n) - 1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return n[int(k)]
    d0 = n[int(f)] * (c - k)
    d1 = n[int(c)] * (k - f)
    return d0 + d1


@register_metric
class QuantileMetric(EmbeddedSubmetrics):
    """
    A metric that can register some values, sequentially, and then calculate quantiles from it

    :param last_calls: last calls to handle() to take into account
    :param quantiles: a sequence of quantiles to return in to_json
    :param aggregate_children: whether to sum up children values (if present)
    :param count_calls: whether to count total amount of calls and total time
    """

    CLASS_NAME = 'quantile'

    def __init__(self, name, root_metric: 'Metric' = None, metric_level: str = None,
                 last_calls: int = 100, quantiles: tp.Sequence[float] = (0.5, 0.95),
                 aggregate_children: bool = True,
                 count_calls: bool = True, *args,
                 **kwargs):
        super().__init__(name, root_metric, metric_level, *args, last_calls=last_calls,
                         quantiles=quantiles, aggregate_children=aggregate_children,
                         count_calls=count_calls,
                         **kwargs)
        self.last_calls = last_calls
        self.calls_queue = collections.deque()
        self.quantiles = quantiles
        self.aggregate_children = aggregate_children
        self.count_calls = count_calls
        self.tot_calls = 0
        self.tot_time = 0

    def _handle(self, time_taken: float, **labels) -> None:
        if self.count_calls:
            self.tot_calls += 1
            self.tot_time += time_taken

        if labels or self.embedded_submetrics_enabled:
            return super()._handle(time_taken, **labels)
        if len(self.calls_queue) == self.last_calls:
            self.calls_queue.pop()
        self.calls_queue.appendleft(time_taken)

    def to_json(self):
        k = self._to_json()
        if self.count_calls:
            if isinstance(k, list):
                return {'count': {'_': self.tot_calls}, 'total': {'_': self.tot_time}, '_': k}
            else:
                k['count'] = {'_': self.tot_calls}
                k['total'] = {'_': self.tot_time}
                if self.enable_timestamp:
                    k['total']['_timestamp'] = k['count']['_timestamp'] = self.last_updated

                return k
        return k

    def _to_json(self) -> dict:
        if self.embedded_submetrics_enabled:
            k = super().to_json()
            if not self.aggregate_children:
                return k
            total_calls = []
            for child in self.children:
                total_calls.extend(child.calls_queue)
            total_calls.sort()
            k = {
                '_': k,
                'sum': self.calculate_quantiles(total_calls)
            }
            if self.enable_timestamp:
                k['_timestamp'] = self.last_updated
            return k
        else:
            return self.calculate_quantiles(self.calls_queue)

    def calculate_quantiles(self, calls_queue):
        output = []
        sorted_calls = sorted(calls_queue)
        for p_val in self.quantiles:
            k = LeafMetric.to_json(self)
            if not sorted_calls:
                k.update(quantile=p_val, _=0.0)
            else:
                k.update(quantile=p_val,
                         _=percentile(sorted_calls, p_val))
            if self.enable_timestamp:
                k['_timestamp'] = self.last_updated
            output.append(k)
        return output

    def measure(self, include_exceptions: bool = True, logging_level: int = RUNTIME,
                value_getter: tp.Callable[[], float] = time.monotonic, **labels):
        """
        A decorator to measure a difference between some value after the method call
        and before it.

        By default, it will measure the execution time.

        Use like:

        >>> call_time = getMetric('root.metric_name.execution_time', 'percentile')
        >>> @call_time.measure()
        >>> def measure_my_execution(args):
        >>>     ...

        If wrapped around generator, it will time it from the first element to the last,
        so beware that it will depend on the speed of the consumer.

        :param include_exceptions: whether to include exceptions
        :param logging_level: one of RUNTIME or DEBUG
        :param value_getter: a callable that takes no arguments and returns a float, which is
            the value
        :param labels: extra labels to call handle() with
        """

        def outer(fun):
            @functools.wraps(fun)
            def inner_normal(*args, **kwargs):
                start_value = value_getter()
                excepted = None
                try:
                    return fun(*args, **kwargs)
                except Exception as e:
                    excepted = e
                finally:
                    value_taken = value_getter() - start_value
                    if excepted is not None and not include_exceptions:
                        raise excepted

                    self.handle(logging_level, value_taken, **labels)

                    if excepted is not None:
                        raise excepted

            @functools.wraps(fun)
            def inner_generator(*args, **kwargs):
                start_value = value_getter()
                excepted = None
                try:
                    for v in fun(*args, **kwargs):
                        yield v
                except Exception as e:
                    excepted = e
                finally:
                    value_taken = value_getter() - start_value
                    if excepted is not None and not include_exceptions:
                        raise excepted

                    self.handle(logging_level, value_taken, **labels)

                    if excepted is not None:
                        raise excepted

            if inspect.isgeneratorfunction(fun):
                return inner_generator
            else:
                return inner_normal

        return outer
