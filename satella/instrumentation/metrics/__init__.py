import itertools
import string
import threading
import typing as tp

from satella.exceptions import MetricAlreadyExists
from .aggregate import AggregateMetric
from .data import MetricDataCollection, MetricData
from .labeled import LabeledMetric
from .metric_types import METRIC_NAMES_TO_CLASSES, MetricLevel, Metric, DEBUG, DISABLED, \
    INHERIT, RUNTIME

__all__ = ['getMetric', 'MetricLevel', 'MetricDataCollection',
           'MetricData', 'Metric', 'DISABLED', 'DEBUG', 'INHERIT', 'RUNTIME',
           'AggregateMetric', 'LabeledMetric']

metrics = {}
metrics_lock = threading.Lock()


def adjust_metric_level_for_root(metric_level: tp.Optional[MetricLevel],
                                 metric_level_to_set_for_children: tp.Optional[MetricLevel]):
    if metric_level is None:
        return MetricLevel.RUNTIME
    elif metric_level_to_set_for_children == MetricLevel.INHERIT:
        return MetricLevel.RUNTIME
    else:
        return metric_level_to_set_for_children


ALLOWED_CHARACTERS = string.ascii_uppercase + string.digits + ':' + '_' + '.'


# noinspection PyPep8Naming
def getMetric(metric_name: str = '',
              metric_type: str = 'base',
              metric_level: tp.Optional[MetricLevel] = None,
              **kwargs):
    """
    Obtain a metric of given name.

    :param metric_name: a metric name. Subsequent nesting levels have to be separated with a dot
    :param metric_type: metric type
    :param metric_level: a metric level to set this metric to.
    :raise MetricAlreadyExists: a metric having this name already exists, but with a different type
    :raise ValueError: metric name contains a forbidden character
    """
    for character in metric_name.upper():
        if character not in ALLOWED_CHARACTERS:
            raise ValueError('Metric name contains a forbidden character %s' % (character,))

    metric_level_to_set_for_children = metric_level or MetricLevel.INHERIT
    name = metric_name.split('.')
    with metrics_lock:
        root_metric = None

        if metric_name in metrics:
            if metrics[metric_name].CLASS_NAME != metric_type:
                raise MetricAlreadyExists('Metric of name %s exists with type %s, which is '
                                          'different that requested %s' % (
                                              metric_name, metrics[metric_name].CLASS_NAME,
                                              metric_type),
                                          name=metric_name,
                                          requested_type=metric_type,
                                          existing_type=metrics[metric_name].CLASS_NAME)

        for name_index, name_part in itertools.chain(((0, ''),), enumerate(name, start=1)):
            tentative_name = '.'.join(name[:name_index])
            if tentative_name not in metrics:
                if tentative_name == '':
                    metric = Metric('',
                                    None,
                                    adjust_metric_level_for_root(metric_level,
                                                                 metric_level_to_set_for_children),
                                    **kwargs)
                    metric.level = MetricLevel.RUNTIME
                    root_metric = metric
                elif metric_name == tentative_name:
                    metric = METRIC_NAMES_TO_CLASSES[metric_type](name_part, root_metric,
                                                                  metric_level, **kwargs)
                else:
                    metric = Metric(name_part, root_metric, metric_level_to_set_for_children,
                                    **kwargs)
                metrics[tentative_name] = metric
                if metric != root_metric:  # prevent infinite recursion errors
                    root_metric.append_child(metric)
            else:
                metric = metrics[tentative_name]
            root_metric = metric

        if metric_level is not None:
            metric.level = metric_level

        return metric
