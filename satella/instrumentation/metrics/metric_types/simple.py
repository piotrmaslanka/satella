import time
import logging
import typing as tp

from .base import EmbeddedSubmetrics
from .registry import register_metric
from ..data import MetricData, MetricDataCollection


logger = logging.getLogger(__name__)


class SimpleMetric(EmbeddedSubmetrics):
    CLASS_NAME = 'string'
    CONSTRUCTOR = str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None

    def _handle(self, *args, **kwargs) -> None:
        if self.embedded_submetrics_enabled or kwargs:
            return super()._handle(*args, **kwargs)
        self.data = self.CONSTRUCTOR(args[0])

    def to_metric_data(self) -> tp.Union[list, dict, str, int, float, None]:
        if self.embedded_submetrics_enabled:
            return super().to_json()
        return MetricDataCollection(
            MetricData(self.name, self.data, self.labels, self.get_timestamp())
        )


@register_metric
class IntegerMetric(SimpleMetric):
    CLASS_NAME = 'int'
    CONSTRUCTOR = int


@register_metric
class FloatMetric(SimpleMetric):
    CLASS_NAME = 'float'
    CONSTRUCTOR = float
