import typing as tp
import time

from ..data import MetricDataCollection, MetricData
from .base import LeafMetric
from .registry import register_metric


@register_metric
class CallableMetric(LeafMetric):
    """
    A metric whose value at any given point in time is the result of it's callable.

    :param value_getter: a callable() that returns a float - the current value of this metric.
        It should be easy and cheap to compute, as this callable will be called each time
        a snapshot of metric state is requested
    """
    CLASS_NAME = 'callable'

    __slots__ = ('callable', )

    def __init__(self, name, root_metric: 'Metric' = None, metric_level: str = None,
                 labels: tp.Optional[dict] = None, internal: bool = False,
                 value_getter: tp.Callable[[], float] = lambda: 0, *args, **kwargs):
        super().__init__(name, root_metric, metric_level, labels, internal, *args, **kwargs)
        self.callable = value_getter

    def _handle(self, *args, **kwargs) -> None:
        raise TypeError('You are not supposed to call this!')

    def to_metric_data(self) -> MetricDataCollection:
        mdc = MetricDataCollection()
        mdc += MetricData(self.name, self.callable(), self.labels, time.time(), self.internal)
        return mdc
