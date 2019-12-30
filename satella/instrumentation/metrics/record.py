import abc

from .metric_types.base import RUNTIME, INHERIT


class BaseRecord(metaclass=abc.ABCMeta):
    def __init__(self, level: str = RUNTIME):
        self.level = level

    def can_be_handled_by(self, metric: 'Metric'):
        run_level = metric.level
        while run_level == INHERIT:
            metric = metric.root_metric
            run_level = metric.level
        else:
            return run_level >= self.level
        raise ValueError('Invalid metric setup - root metric is in inherit mode!')
