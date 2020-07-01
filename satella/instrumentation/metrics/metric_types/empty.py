from .base import Metric
from .registry import register_metric
from ..data import MetricDataCollection


@register_metric
class EmptyMetric(Metric):
    """
    A metric that disregards all data that it's fed, and outputs nothing.

    A placeholder for the times when you configure metrics and decide to leave some of them out
    blank.
    """
    __slots__ = ()

    CLASS_NAME = 'empty'

    def _handle(self, *args, **kwargs) -> None:
        pass

    def to_metric_data(self) -> MetricDataCollection:
        return MetricDataCollection()
