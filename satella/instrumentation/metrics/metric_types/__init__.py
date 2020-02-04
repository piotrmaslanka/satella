from .base import Metric, LeafMetric
from .cps import ClicksPerTimeUnitMetric
from .simple import StringMetric, IntegerMetric, FloatMetric

ALL_METRICS = [
    Metric,
    LeafMetric,
    StringMetric,
    IntegerMetric,
    FloatMetric,
    ClicksPerTimeUnitMetric
]

METRIC_NAMES_TO_CLASSES = {
    metric.CLASS_NAME: metric for metric in ALL_METRICS
}
