import typing as tp

from .base import EmbeddedSubmetrics
from .measurable_mixin import MeasurableMixin
from .registry import register_metric
from ..data import MetricData, MetricDataContainer


class SimpleMetric(EmbeddedSubmetrics):
    __slots__ = ('data', )

    CLASS_NAME = 'string'
    CONSTRUCTOR = str

    def __init__(self, *args, **kwargs):
        kwargs.update(metric_type='gauge')
        super().__init__(*args, **kwargs)
        self.data = None                # type: tp.Any

    def _handle(self, value, **labels) -> None:
        if self.embedded_submetrics_enabled or labels:
            return super()._handle(value, **labels)
        self.data = self.CONSTRUCTOR(value)

    def to_metric_data_container(self) -> MetricDataContainer:
        if self.embedded_submetrics_enabled:
            return super().to_metric_data_container()
        mdc = super().to_metric_data_container()
        return mdc + MetricData(self.get_fully_qualified_name(), self.data, self.labels)


@register_metric
class IntegerMetric(SimpleMetric):
    CLASS_NAME = 'int'
    CONSTRUCTOR = int


@register_metric
class FloatMetric(SimpleMetric, MeasurableMixin):
    CLASS_NAME = 'float'
    CONSTRUCTOR = float
