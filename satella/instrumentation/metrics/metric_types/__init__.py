from .base import Metric, LeafMetric
from .cps import ClicksPerTimeUnitMetric
from .simple import IntegerMetric, FloatMetric
from .percentile import PercentileMetric

ALL_METRICS = [
    Metric,
    LeafMetric,
    IntegerMetric,
    FloatMetric,
    ClicksPerTimeUnitMetric,
    PercentileMetric
]

METRIC_NAMES_TO_CLASSES = {
    metric.CLASS_NAME: metric for metric in ALL_METRICS
}
