import typing as tp

from .base import EmbeddedSubmetrics
from .measurable_mixin import MeasurableMixin
from .registry import register_metric
from ..data import MetricData, MetricDataCollection


class SimpleMetric(EmbeddedSubmetrics):
    __slots__ = ('data',)

    CLASS_NAME = 'string'
    CONSTRUCTOR = str
    DEFAULT_VALUE = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = self.DEFAULT_VALUE  # type: tp.Any

    def _handle(self, value, **labels) -> None:
        if self.embedded_submetrics_enabled or labels:
            return super()._handle(value, **labels)
        self.data = self.CONSTRUCTOR(value)

    def to_metric_data(self) -> tp.Union[list, dict, str, int, float, None]:
        if self.embedded_submetrics_enabled:
            return super().to_metric_data()
        return MetricDataCollection(
            MetricData(self.name, self.data, self.labels, self.get_timestamp(), self.internal)
        )


@register_metric
class IntegerMetric(SimpleMetric):
    CLASS_NAME = 'int'
    CONSTRUCTOR = int
    DEFAULT_VALUE = 0


@register_metric
class FloatMetric(SimpleMetric, MeasurableMixin):
    CLASS_NAME = 'float'
    CONSTRUCTOR = float
    DEFAULT_VALUE = 0.0
