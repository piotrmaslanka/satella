import logging
from .base import EmbeddedSubmetrics
from ..data import  MetricData, MetricDataCollection
from .registry import register_metric
logger = logging.getLogger(__name__)


@register_metric
class CounterMetric(EmbeddedSubmetrics):
    """
    A counter that can be adjusted by a given value.

    :param sum_children: whether to sum up all calls to children
    :param count_calls: count the amount of calls to handle()
    """
    CLASS_NAME = 'counter'

    def __init__(self, name, root_metric: 'Metric' = None, metric_level: str = None,
                 sum_children: bool = True,
                 count_calls: bool = False, *args, **kwargs):
        super().__init__(name, root_metric, metric_level, sum_children=sum_children,
                         count_calls=count_calls, *args, **kwargs)
        self.sum_children = sum_children
        self.count_calls = count_calls
        self.calls = 0
        self.value = 0

    def to_metric_data(self) -> MetricDataCollection:
        if self.embedded_submetrics_enabled:
            k = super().to_metric_data()
            if self.sum_children:
                k += MetricData(self.name+'.sum', self.value, self.labels, self.get_timestamp())
            if self.count_calls:
                k += MetricData(self.name+'.count', self.calls, self.labels, self.get_timestamp())
            return k

        p = super().to_metric_data()
        p.set_value(self.value)
        if self.count_calls:
            p += MetricData(self.name+'.count', self.calls, self.labels, self.get_timestamp())

        return p

    def _handle(self, delta: float = 0, **labels):
        if self.embedded_submetrics_enabled or labels:
            if self.sum_children:
                self.value += delta
            self.calls += 1
            return super()._handle(delta, **labels)

        self.value += delta
        self.calls += 1
