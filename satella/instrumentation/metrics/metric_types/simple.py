import typing as tp

from .base import LeafMetric


class SimpleMetric(LeafMetric):
    CLASS_NAME = 'string'
    CONSTRUCTOR = str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None

    def handle(self, level, data):
        if self.can_process_this_level(level):
            self.data = self.CONSTRUCTOR(data)

    def to_json(self) -> tp.Union[list, dict, str, int, float, None]:
        p = {'_': self.data}
        p.update(super().to_json())
        return p


class StringMetric(SimpleMetric):
    pass


class IntegerMetric(SimpleMetric):
    CLASS_NAME = 'int'
    CONSTRUCTOR = int


class FloatMetric(SimpleMetric):
    CLASS_NAME = 'float'
    CONSTRUCTOR = float
