import typing as tp
from .base import EmbeddedSubmetrics, MetricLevel
from .measurable_mixin import MeasurableMixin
from ..data import MetricData, MetricDataCollection, MetricDataContainer
from .registry import register_metric


@register_metric
class CounterMetric(EmbeddedSubmetrics, MeasurableMixin):
    """
    A counter that can be adjusted by a given value.

    :param sum_children: whether to sum up all calls to children
    :param count_calls: count the amount of calls to handle()
    """
    __slots__ = ('sum_children', 'count_calls', 'calls', 'value')

    CLASS_NAME = 'counter'

    def __init__(self, name, root_metric: 'Metric' = None,
                 metric_level: tp.Optional[MetricLevel] = None,
                 internal: bool = False,
                 sum_children: bool = True,
                 count_calls: bool = False, *args, **kwargs):
        super().__init__(name, root_metric, metric_level, internal=internal,
                         sum_children=sum_children, count_calls=count_calls, metric_type='counter',
                         *args, **kwargs)
        self.sum_children = sum_children            # type: bool
        self.count_calls = count_calls              # type: bool
        self.calls = 0                              # type: int
        self.value = 0                              # type: float

    def to_metric_data_container(self) -> MetricDataContainer:
        if self.embedded_submetrics_enabled:
            k = super().to_metric_data()
            if self.sum_children:
                k += MetricData(self.name+'.total', self.value, self.labels, self.get_timestamp(),
                                self.internal)
            if self.count_calls:
                k += MetricData(self.name+'.count', self.calls, self.labels, self.get_timestamp(),
                                self.internal)
            return k
        else:
            p = super().to_metric_data_container()
            if self.count_calls:
                p += MetricData(self.name+'.count', self.calls, self.labels)
            p += MetricData(self.name, self.value, self.labels)

            return p

    def _handle(self, delta: float = 0, **labels):
        if self.embedded_submetrics_enabled or labels:
            if self.sum_children:
                self.value += delta
            self.calls += 1
            return super()._handle(delta, **labels)

        self.value += delta
        self.calls += 1
