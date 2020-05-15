import typing as tp

from .metric_types import CallableMetric
from .metric_types.measurable_mixin import MeasurableMixin
from .metric_types.base import Metric, MetricLevel


class LabeledMetric(Metric, MeasurableMixin):
    """
    A wrapper to another metric that will always call it's .runtime and .handle with some predefined labels

    Use like:

    >>> a = getMetric('a', 'counter')
    >>> b = LabeledMetric(a, key=5)

    Then this:

    >>> a.runtime(1, key=5)

    Will be equivalent to this:

    >>> b.runtime(1)
    """
    __slots__ = ('metric_to_wrap', 'labels', 'callable')

    def __init__(self, metric_to_wrap, **labels):
        self.metric_to_wrap = metric_to_wrap
        self.labels = labels
        self.callable = labels.pop('callable', lambda: 0)

        if isinstance(metric_to_wrap, CallableMetric):
            metric_to_wrap.register_labeled_metric(self)

    def handle(self, level: tp.Union[int, MetricLevel], *args, **kwargs) -> None:
        kwargs.update(self.labels)
        self.metric_to_wrap.handle(level, *args, **kwargs)


