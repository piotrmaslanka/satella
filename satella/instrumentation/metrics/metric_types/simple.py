import typing as tp

from .base import Metric


class SimpleMetric(Metric):
    CLASS_NAME = 'string'
    CONSTRUCTOR = str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None

    def append_child(self, metric: 'Metric'):
        raise TypeError('This metric cannot contain children!')

    def handle(self, level, data):
        if self.can_process_this_level(level):
            self.data = self.CONSTRUCTOR(data)

    def to_json(self) -> tp.Union[list, dict, str, int, float, None]:
        return self.data


class StringMetric(SimpleMetric):
    pass


class IntegerMetric(SimpleMetric):
    CLASS_NAME = 'int'
    CONSTRUCTOR = int


class FloatMetric(SimpleMetric):
    CLASS_NAME = 'float'
    CONSTRUCTOR = float
