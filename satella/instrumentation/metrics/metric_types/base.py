import typing as tp
import logging
import copy
import time
import functools
import inspect
from ..data import MetricData, MetricDataCollection
from .registry import register_metric

logger = logging.getLogger(__name__)

DISABLED = 1
RUNTIME = 2
DEBUG = 3
INHERIT = 4


class Metric:
    """
    Container for child metrics. A base metric class, as well as the default metric.

    Switch levels by setting metric.level to a proper value

    :param enable_timestamp: append timestamp of last update to the metric
    """
    CLASS_NAME = 'base'

    def get_fully_qualified_name(self):
        data = []
        metric = self
        while metric.root_metric is not None:
            data.append(metric.name)
            metric = metric.root_metric
        return '.'.join(reversed(data))

    def reset(self) -> None:
        """
        Delete all child metrics that this metric contains.

        Also, if called on root metric, sets the runlevel to RUNTIME
        """
        from satella.instrumentation import metrics
        if self.name == '':
            with metrics.metrics_lock:
                metrics.metrics = {}
                metrics.level = RUNTIME
        else:
            with metrics.metrics_lock:
                metrics.metrics = {k: v for k, v in metrics.metrics.items() if
                                   not k.startswith(self.get_fully_qualified_name() + '.')}
                del metrics.metrics[self.get_fully_qualified_name()]
        self.children = []

    def __init__(self, name, root_metric: 'Metric' = None, metric_level: str = None,
                 *args, **kwargs):
        """When reimplementing the method, remember to pass kwargs here!"""
        self.name = name
        self.root_metric = root_metric
        if metric_level is None:
            if self.name == '':
                metric_level = RUNTIME
            else:
                metric_level = INHERIT
        self._level = metric_level
        self.enable_timestamp = kwargs.get('enable_timestamp', False)
        if self.enable_timestamp:
            self.last_updated = time.time()

        assert not (
                self.name == '' and self.level == INHERIT), 'Unable to set INHERIT for root metric!'
        self.children = []

    def get_timestamp(self) -> tp.Optional[float]:
        """Return this timestamp, or None if no timestamp support is enabled"""
        return self.last_updated if self.enable_timestamp else None

    def __str__(self) -> str:
        return self.name

    @property
    def level(self) -> int:
        metric = self
        while metric._level == INHERIT:
            metric = metric.root_metric
        return metric._level

    @level.setter
    def level(self, value: int) -> None:
        assert not (value == INHERIT and self.name == ''), 'Cannot set INHERIT for the root metric!'
        self._level = value

    def append_child(self, metric: 'Metric'):
        self.children.append(metric)

    def can_process_this_level(self, target_level: int) -> bool:
        return self.level >= target_level

    def to_metric_data(self) -> MetricDataCollection:
        output = MetricDataCollection()
        for child in self.children:
            output += child.to_metric_data()
        output.prefix_with(self.name)

        if self.enable_timestamp:
            output.set_timestamp(self.last_updated)

        return output

    def _handle(self, *args, **kwargs) -> None:
        """
        Override me!
        """
        raise NotImplementedError('This is an abstract method!')

    def handle(self, level: int, *args, **kwargs) -> None:
        if self.can_process_this_level(level):
            if self.enable_timestamp:
                self.last_updated = time.time()
            return self._handle(*args, **kwargs)

    def debug(self, *args, **kwargs):
        self.handle(DEBUG, *args, **kwargs)

    def runtime(self, *args, **kwargs):
        self.handle(RUNTIME, *args, **kwargs)


class LeafMetric(Metric):
    """
    A metric capable of generating only leaf entries.

    You cannot hook up any children to a leaf metric.
    """
    def __init__(self, name, root_metric: 'Metric' = None, metric_level: str = None,
                 labels: tp.Optional[dict] = None, *args, **kwargs):
        super().__init__(name, root_metric, metric_level, *args, **kwargs)
        self.labels = labels or {}
        assert '_timestamp' not in self.labels, 'Cannot make a label called _timestamp!'

    def to_metric_data(self) -> MetricDataCollection:
        return MetricDataCollection(MetricData(self.name, None, self.labels))

    def append_child(self, metric: 'Metric'):
        raise TypeError('This metric cannot contain children!')


class EmbeddedSubmetrics(LeafMetric):
    """
    A metric that can optionally accept some labels in it's handle, and this will be counted as a
    separate metric.
    For example:

    >>> metric = getMetric('root.test.IntValue', 'int', enable_timestamp=False)
    >>> metric.handle(2, label='key')
    >>> metric.handle(3, label='value')

    If you try to inherit from it, refer to :py:class:`.simple.IntegerMetric` to see how to do it.
    And please pass all the arguments received from child class into this constructor, as this
    constructor actually stores them!
    Refer to :py:class:`.cps.ClicksPerTimeUnitMetric` on how to do that.
    """
    def __init__(self, name, root_metric: 'Metric' = None, metric_level: str = None,
                 labels: tp.Optional[dict] = None, *args, **kwargs):
        super().__init__(name, root_metric, metric_level, labels, *args, **kwargs)
        self.args = args
        self.kwargs = kwargs
        self.embedded_submetrics_enabled = False        # to check for in children
        self.children_mapping = {}
        self.last_updated = time.time()

    def _handle(self, *args, **labels):
        if self.enable_timestamp:
            self.last_updated = time.time()

        key = tuple(sorted(labels.items()))
        if key:
            self.embedded_submetrics_enabled = True
        else:
            return

        if key in self.children_mapping:
            # noinspection PyProtectedMember
            self.children_mapping[key]._handle(*args)
        else:
            clone = self.clone(labels)
            self.children_mapping[key] = clone
            self.children.append(clone)
            # noinspection PyProtectedMember
            self.children_mapping[key]._handle(*args)

    def to_metric_data(self) -> MetricDataCollection:
        if self.embedded_submetrics_enabled:
            v = MetricDataCollection()
            for child in self.children:
                v = v + child.to_metric_data()
            return v
        else:
            return super().to_metric_data()

    def clone(self, labels: dict) -> 'LeafMetric':
        """
        Return a fresh instance of this metric, with it's parent being set to this metric
        and having a particular set of labels, and being of level INHERIT.
        """

        return self.__class__(self.name, self, INHERIT, *self.args, labels=labels, **self.kwargs)


class MeasurableMixin:
    """
    Add a .measure() method, useful for HistogramMetric and SummaryMetric
    """

    def measure(self, include_exceptions: bool = True, logging_level: int = RUNTIME,
                value_getter: tp.Callable[[], float] = time.monotonic, **labels):
        """
        A decorator to measure a difference between some value after the method call
        and before it.

        By default, it will measure the execution time.

        Use like:

        >>> call_time = getMetric('root.metric_name.execution_time', 'summary')
        >>> @call_time.measure()
        >>> def measure_my_execution(args):
        >>>     ...

        If wrapped around generator, it will time it from the first element to the last,
        so beware that it will depend on the speed of the consumer.

        :param include_exceptions: whether to include exceptions
        :param logging_level: one of RUNTIME or DEBUG
        :param value_getter: a callable that takes no arguments and returns a float, which is
            the value
        :param labels: extra labels to call handle() with
        """

        def outer(fun):
            @functools.wraps(fun)
            def inner_normal(*args, **kwargs):
                start_value = value_getter()
                excepted = None
                try:
                    return fun(*args, **kwargs)
                except Exception as e:
                    excepted = e
                finally:
                    value_taken = value_getter() - start_value
                    if excepted is not None and not include_exceptions:
                        raise excepted

                    self.handle(logging_level, value_taken, **labels)

                    if excepted is not None:
                        raise excepted

            @functools.wraps(fun)
            def inner_generator(*args, **kwargs):
                start_value = value_getter()
                excepted = None
                try:
                    for v in fun(*args, **kwargs):
                        yield v
                except Exception as e:
                    excepted = e
                finally:
                    value_taken = value_getter() - start_value
                    if excepted is not None and not include_exceptions:
                        raise excepted

                    self.handle(logging_level, value_taken, **labels)

                    if excepted is not None:
                        raise excepted

            if inspect.isgeneratorfunction(fun):
                return inner_generator
            else:
                return inner_normal

        return outer


@register_metric
class EmptyMetric(Metric):
    """
    A metric that disregards all data that it's fed, and outputs nothing.

    A placeholder for the times when you configure metrics and decide to leave some of them out blank.
    """
    CLASS_NAME = 'empty'

    def _handle(self, *args, **kwargs) -> None:
        pass

    def to_metric_data(self) -> MetricDataCollection:
        return MetricDataCollection()
