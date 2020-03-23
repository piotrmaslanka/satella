import collections
import warnings

import typing as tp

import math

from .base import EmbeddedSubmetrics, MetricLevel
from .measurable_mixin import MeasurableMixin
from .registry import register_metric
from ..data import MetricData, MetricDataCollection


# shamelessly taken from
# http://code.activestate.com/recipes/511478-finding-the-percentile-of-the-values/)
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
class SummaryMetric(EmbeddedSubmetrics, MeasurableMixin):
    """
    A metric that can register some values, sequentially, and then calculate quantiles from it.
    It calculates configurable quantiles over a sliding window of amount of measurements.

    :param last_calls: last calls to handle() to take into account
    :param quantiles: a sequence of quantiles to return in to_metric_data
    :param aggregate_children: whether to sum up children values (if present)
    :param count_calls: whether to count total amount of calls and total time
    """
    __slots__ = ('last_calls', 'calls_queue', 'quantiles', 'aggregate_children',
                 'count_calls', 'tot_calls', 'tot_time')

    CLASS_NAME = 'summary'

    def __init__(self, name, root_metric: 'Metric' = None,
                 metric_level: tp.Optional[MetricLevel] = None,
                 internal: bool = False,
                 last_calls: int = 100, quantiles: tp.Sequence[float] = (0.5, 0.95),
                 aggregate_children: bool = True,
                 count_calls: bool = True, *args,
                 **kwargs):
        super().__init__(name, root_metric, metric_level, *args, internal=internal,
                         last_calls=last_calls,  quantiles=quantiles,
                         aggregate_children=aggregate_children, count_calls=count_calls,
                         **kwargs)
        self.last_calls = last_calls                    # type: int
        self.calls_queue = collections.deque()          # type: tp.List[float]
        self.quantiles = quantiles                      # type: tp.List[float]
        self.aggregate_children = aggregate_children    # type: bool
        self.count_calls = count_calls                  # type: bool
        self.tot_calls = 0                              # type: int
        self.tot_time = 0                               # type: float

    def _handle(self, time_taken: float, **labels) -> None:
        if self.count_calls:
            self.tot_calls += 1
            self.tot_time += time_taken

        if labels or self.embedded_submetrics_enabled:
            return super()._handle(time_taken, **labels)

        if len(self.calls_queue) == self.last_calls:
            self.calls_queue.pop()

        self.calls_queue.appendleft(time_taken)

    def to_metric_data(self) -> MetricDataCollection:
        k = self._to_metric_data()
        if self.count_calls:
            k += MetricData(self.name+'.count', self.tot_calls, self.labels, self.get_timestamp(),
                            self.internal)
            k += MetricData(self.name+'.sum', self.tot_time, self.labels, self.get_timestamp(),
                            self.internal)
        return k

    def _to_metric_data(self) -> MetricDataCollection:
        if self.embedded_submetrics_enabled:
            k = super().to_metric_data()
            if self.aggregate_children:
                total_calls = []
                for child in self.children:
                    total_calls.extend(child.calls_queue)
                total_calls.sort()

                q = self.calculate_quantiles(total_calls)
                q.postfix_with('total')
                k += q

            if self.count_calls:
                k += MetricData(self.name+'.count', self.tot_calls, self.labels,
                                self.get_timestamp(), self.internal)
                k += MetricData(self.name+'.sum', self.tot_time, self.labels, self.get_timestamp(),
                                self.internal)

            return k
        else:
            return self.calculate_quantiles(self.calls_queue)

    def calculate_quantiles(self, calls_queue) -> MetricDataCollection:
        output = MetricDataCollection()
        sorted_calls = sorted(calls_queue)
        for p_val in self.quantiles:
            if not sorted_calls:
                output += MetricData(self.name, 0.0, {'quantile': p_val, **self.labels},
                                     self.get_timestamp(), self.internal)
            else:
                output += MetricData(self.name, percentile(sorted_calls, p_val),
                                     {'quantile': p_val, **self.labels}, self.get_timestamp(),
                                     self.internal)
        return output


@register_metric
class QuantileMetric(SummaryMetric):
    CLASS_NAME = 'quantile'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn('quantile is deprecated; use summary instead', DeprecationWarning)
