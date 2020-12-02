import collections
import time
import typing as tp
import warnings

from .base import EmbeddedSubmetrics
from .registry import register_metric
from ..data import MetricData, MetricDataCollection


@register_metric
class ClicksPerTimeUnitMetric(EmbeddedSubmetrics):
    """
    This tracks the amount of calls to handle() during the last time periods, as specified by time_unit_vectors
    (in seconds). You may specify multiple time periods as consequent entries in the list.

    By default (if you do not specify otherwise) this will track calls made during the last second.

    .. deprecated:: 2.14.22
        Use :class:`~satella.instrumentation.metrics.metric_types.CounterMetric` instead
    """
    __slots__ = ('last_clicks', 'aggregate_children', 'cutoff_period', 'time_unit_vectors')

    CLASS_NAME = 'cps'

    def __init__(self, *args, time_unit_vectors: tp.Optional[tp.List[float]] = None,
                 aggregate_children: bool = True, internal: bool = False, **kwargs):
        warnings.warn('cps is deprecated and will be removed in Satella 3.0, '
                      'use a counter and calculate a rate() from it instead',
                      DeprecationWarning)
        super().__init__(*args, internal=internal, time_unit_vectors=time_unit_vectors, **kwargs)
        time_unit_vectors = time_unit_vectors or [1]
        self.last_clicks = collections.deque()  # type: tp.List[float]
        self.aggregate_children = aggregate_children  # type: bool
        self.cutoff_period = max(time_unit_vectors)  # type: int
        self.time_unit_vectors = time_unit_vectors  # type: tp.List[int]

    def _handle(self, **labels) -> None:
        if labels or self.embedded_submetrics_enabled:
            return super()._handle(**labels)

        mono_time = time.monotonic()
        self.last_clicks.append(time.monotonic())
        try:
            while self.last_clicks[0] <= mono_time - self.cutoff_period:
                self.last_clicks.popleft()
        except IndexError:
            pass

    def to_metric_data(self) -> tp.List[int]:
        if self.embedded_submetrics_enabled:
            k = super().to_metric_data()
            if not self.aggregate_children:
                return k
            else:
                last_clicks = []
                for child in self.children:
                    last_clicks.extend(child.last_clicks)

                sum_data = self.count_vectors(last_clicks)
                sum_data.postfix_with('total')

                return k + sum_data

        return self.count_vectors(self.last_clicks)

    def count_vectors(self, last_clicks) -> MetricDataCollection:
        count_map = [0] * len(self.time_unit_vectors)
        mono_time = time.monotonic()
        time_unit_vectors = [mono_time - v for v in self.time_unit_vectors]

        for v in last_clicks:
            for index, cutoff in enumerate(time_unit_vectors):
                if v >= cutoff:
                    count_map[index] += 1

        output = []
        for time_unit, count in zip(self.time_unit_vectors, count_map):
            output.append(MetricData(self.name, count, {'period': time_unit, **self.labels},
                                     self.get_timestamp(), self.internal))

        return MetricDataCollection(output)
