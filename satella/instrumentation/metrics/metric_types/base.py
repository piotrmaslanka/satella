import typing as tp

from satella.json import JSONAble

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

    def __init__(self, name, root_metric: 'Metric' = None, metric_level: str = None, **kwargs):
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

    def handle(self, level: int, *args, **kwargs) -> None:
        """Override me!"""
        raise TypeError('A collection of metrics is not meant to get .handle() called!')

    def debug(self, *args, **kwargs):
        self.handle(DEBUG, *args, **kwargs)

    def runtime(self, *args, **kwargs):
        self.handle(RUNTIME, *args, **kwargs)
