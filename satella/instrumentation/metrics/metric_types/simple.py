import typing as tp

from .base import EmbeddedSubmetrics


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

    def to_json(self) -> tp.Union[list, dict, str, int, float, None]:
        if self.embedded_submetrics_enabled:
            return super().to_json()
        p = super().to_json()
        p['_'] = self.data
        return p


class StringMetric(SimpleMetric):
    pass


class IntegerMetric(SimpleMetric):
    CLASS_NAME = 'int'
    CONSTRUCTOR = int


class FloatMetric(SimpleMetric):
    CLASS_NAME = 'float'
    CONSTRUCTOR = float
