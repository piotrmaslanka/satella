import typing as tp
import copy
from abc import abstractmethod, ABCMeta
from satella.json import JSONAble
from satella.coding import for_argument


DISABLED = 1
RUNTIME = 2
DEBUG = 3
INHERIT = 4


class Metric(JSONAble):
    """
    A base metric class
    """
    CLASS_NAME = 'base'

    def reset(self) -> None:
        """Delete all child metrics that this metric contains"""
        from satella.instrumentation import metrics
        if self.name == '':
            metrics.metrics = {}
        else:
            metrics.metrics = {k: v for k, v in metrics.metrics.items() if
                               not k.startswith(self.name + '.')}
            del metrics.metrics[self.name]
        self.children = []

    def __init__(self, name, root_metric: 'Metric' = None, metric_level: str = None):
        """When reimplementing the method, remember to pass kwargs here!"""
        self.name = name
        self.root_metric = root_metric
        self.level = metric_level or RUNTIME
        assert not (
                self.name == '' and self.level == INHERIT), 'Unable to set INHERIT for root metric!'
        self.children = []

    def __str__(self) -> str:
        return self.name

    def append_child(self, metric: 'Metric'):
        self.children.append(metric)

    def can_process_this_level(self, target_level: int) -> bool:
        metric = self
        while metric.level == INHERIT:
            # this is bound to terminate, since it is not possible to set metric_level of INHERIT on root
            metric = metric.root_metric
        return metric.level >= target_level

    def switch_level(self, level: int) -> None:
        assert not (self.name == '' and level == INHERIT), 'Unable to set INHERIT for root metric!'
        self.level = level

    def to_json(self) -> tp.Union[list, dict, str, int, float, None]:
        return {
            child.name[len(self.name) + 1 if len(self.name) > 0 else 0:]: child.to_json() for child
            in self.children
        }

    def _handle(self, *args, **kwargs) -> None:
        """
        Override me!
        """
        raise NotImplementedError('This is an abstract method!')

    def handle(self, level: int, *args, **kwargs) -> None:
        if self.can_process_this_level(level):
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
                 labels: tp.Optional[dict] = None):
        super().__init__(name, root_metric, metric_level)
        self.labels = labels or {}

    def to_json(self) -> dict:
        return copy.copy(self.labels)

    def append_child(self, metric: 'Metric'):
        raise TypeError('This metric cannot contain children!')


class EmbeddedSubmetrics(LeafMetric):
    """
    A metric that can optionally accept some labels in it's handle, and this will be counted as a
    separate metric.
    For example:

    >>> metric = getMetric('root.test.IntValue', 'int')
    >>> metric.handle(2, label='key')
    >>> metric.handle(3, label='value')
    >>> assert metric.to_json() == [{'label': 'key', '_': 2}, {'label': 'value', '_': 3}]

    If you try to inherit from it, refer to :py:class:`.simple.IntegerMetric` to see how to do it.
    And please pass all the arguments received from child class into this constructor, as this
    constructor actually stores them!
    Refer to :py:class:`.cps.ClicksPerTimeUnitMetric` on how to do that.
    """
    def __init__(self, name, root_metric: 'Metric' = None, metric_level: str = None,
                 labels: tp.Optional[dict] = None, *args, **kwargs):
        super().__init__(name, root_metric, metric_level, labels)
        self.args = args
        self.kwargs = kwargs
        self.embedded_submetrics_enabled = False        # to check for in children
        self.children_mapping = {}

    def _handle(self, value, **labels):
        key = tuple(sorted(labels.items()))
        if key:
            self.embedded_submetrics_enabled = True
        else:
            return

        if key in self.children_mapping:
            # noinspection PyProtectedMember
            self.children_mapping[key]._handle(value)
        else:
            clone = self.clone(labels)
            self.children_mapping[key] = clone
            self.children.append(clone)
            # noinspection PyProtectedMember
            self.children_mapping[key]._handle(value)

    def to_json(self) -> list:
        if self.embedded_submetrics_enabled:
            return [child.to_json() for child in self.children]
        else:
            return super().to_json()

    def clone(self, labels: dict) -> 'LeafMetric':
        """
        Return a fresh instance of this metric, with it's parent being set to this metric
        and having a particular set of labels, and being of level INHERIT.
        """

        return self.__class__(self.name, self, INHERIT, *self.args, labels=labels, **self.kwargs)
