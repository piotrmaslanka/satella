import typing as tp
from .base import Metric
from .simple import StringMetric, IntegerMetric, FloatMetric

ALL_METRICS = [
    Metric,
    StringMetric,
    IntegerMetric,
    FloatMetric
]

METRIC_NAMES_TO_CLASSES = {
    metric.CLASS_NAME: metric for metric in ALL_METRICS
}