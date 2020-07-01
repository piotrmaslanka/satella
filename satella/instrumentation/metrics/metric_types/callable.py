import copy
import time
import typing as tp

from .base import LeafMetric, MetricLevel
from .registry import register_metric
from ..data import MetricDataCollection, MetricData


@register_metric
class CallableMetric(LeafMetric):
    """
    A metric whose value at any given point in time is the result of it's callable.

    :param value_getter: a callable() that returns a float - the current value of this metric.
        It should be easy and cheap to compute, as this callable will be called each time
        a snapshot of metric state is requested
    """
    CLASS_NAME = 'callable'

    __slots__ = ('callable', 'labeled_metrics')

    def __init__(self, name, root_metric: 'Metric' = None,
                 metric_level: tp.Optional[MetricLevel] = None,
                 labels: tp.Optional[dict] = None, internal: bool = False,
                 value_getter: tp.Optional[tp.Callable[[], float]] = None, *args, **kwargs):
        super().__init__(name, root_metric, metric_level, labels, internal, *args, **kwargs)
        self.callable = value_getter
        self.labeled_metrics = []

    def register_labeled_metric(self, labeled_metric):
        self.labeled_metrics.append(labeled_metric)

    def _handle(self, *args, **kwargs) -> None:
        raise TypeError('You are not supposed to call this!')

    def to_metric_data(self) -> MetricDataCollection:
        mdc = MetricDataCollection()
        for labeled_metric in self.labeled_metrics:
            labels = copy.copy(self.labels)
            labels.update(labeled_metric.labels)
            mdc += MetricData(self.name, labeled_metric.callable(), labels, time.time(),
                              self.internal)

        if self.callable:
            mdc += MetricData(self.name, self.callable(), self.labels, time.time(), self.internal)

        return mdc
