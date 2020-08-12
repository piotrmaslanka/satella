import time
import typing as tp

from .base import LeafMetric
from .registry import register_metric
from ..data import MetricDataCollection, MetricData


@register_metric
class UptimeMetric(LeafMetric):
    """
    A metric that gives the difference between current value of time_getter
    and it's value at the initialization of this metric

    :param time_getter: a callable/0 that returns a float, the notion of the time
        passing. By default it's a safe time.monotonic
    """
    __slots__ = ('time_getter', 'basic_time')

    CLASS_NAME = 'uptime'

    def __init__(self, *args, time_getter: tp.Callable[[], float] = time.monotonic,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.time_getter = time_getter
        self.basic_time = time_getter()

    def _handle(self, *args, **kwargs) -> None:
        raise TypeError('You are not supposed to call this!')

    def to_metric_data(self) -> MetricDataCollection:
        return MetricDataCollection(
            MetricData(self.name,
                       self.time_getter() - self.basic_time,
                       self.labels, self.get_timestamp(), self.internal)
        )
