import itertools
import logging
import threading
import typing as tp

logger = logging.getLogger(__name__)
from .metric_types import METRIC_NAMES_TO_CLASSES, RUNTIME, DISABLED, DEBUG, INHERIT, Metric
from .data import MetricDataCollection, MetricData

__all__ = ['getMetric', 'DISABLED', 'RUNTIME', 'DEBUG', 'INHERIT', 'MetricDataCollection',
           'MetricData', 'Metric']

metrics = {}
metrics_lock = threading.Lock()


# noinspection PyPep8Naming
def getMetric(metric_name: str = '',
              metric_type: str = 'base',
              metric_level: tp.Optional[str] = None,
              **kwargs):
    """
    Obtain a metric of given name.

    metric_name --  must be a module name
    """
    metric_level_to_set_for_children = metric_level or INHERIT
    name = metric_name.split('.')
    with metrics_lock:
        root_metric = None
        for name_index, name_part in itertools.chain(((0, ''), ), enumerate(name, start=1)):
            tentative_name = '.'.join(name[:name_index])
            if tentative_name not in metrics:
                if tentative_name == '':
                    # initialize the root metric
                    if metric_level is None:
                        metric_level_to_set_for_root = RUNTIME
                    elif metric_level_to_set_for_children == INHERIT:
                        metric_level_to_set_for_root = RUNTIME
                    else:
                        metric_level_to_set_for_root = metric_level_to_set_for_children
                    metric = Metric('', None, metric_level_to_set_for_root, **kwargs)
                    metric.level = RUNTIME
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
