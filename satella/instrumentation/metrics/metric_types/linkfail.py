import collections
import typing as tp

from .base import EmbeddedSubmetrics, MetricLevel
from .registry import register_metric
from ..data import MetricDataCollection, MetricData


@register_metric
class LinkfailMetric(EmbeddedSubmetrics):
    """
    Metric that measures whether given link is operable.

    :param consecutive_failures_to_offline: consecutive failures needed for link to become offline
    :param consecutive_successes_to_online: consecutive successes needed for link to become online
        after a failure
    :param callback_on_online: callback that accepts an address of a link that becomes online
        and labels
    :param callback_on_offline: callback that accepts an address of a link that becomes offline
        and labels
    """
    __slots__ = ('working', 'consecutive_failures', 'consecutive_successes',
                 'callback_on_online', 'callback_on_offline',
                 'consecutive_failures_to_offline', 'consecutive_successes_to_online')

    CLASS_NAME = 'linkfail'

    def __init__(self, name: str, root_metric: 'Metric' = None,
                 metric_level: tp.Optional[MetricLevel] = None,
                 labels: tp.Optional[dict] = None, internal: bool = False,
                 consecutive_failures_to_offline: int = 100,
                 consecutive_successes_to_online: int = 10,
                 callback_on_online: tp.Callable[[int, dict], None] = lambda a, b: None,
                 callback_on_offline: tp.Callable[[int, dict], None] = lambda a, b: None,
                 *args, **kwargs):
        super().__init__(name, root_metric, metric_level, labels, internal, *args,
                         consecutive_failures_to_offline=consecutive_failures_to_offline,
                         consecutive_successes_to_online=consecutive_successes_to_online,
                         callback_on_offline=callback_on_offline,
                         callback_on_online=callback_on_online,
                         **kwargs)
        self.working = collections.defaultdict(lambda: True)  # type: tp.Dict[int, bool]
        self.consecutive_failures = collections.defaultdict(lambda: 0)  # type: tp.Dict[int, int]
        self.consecutive_successes = collections.defaultdict(lambda: 0)  # type: tp.Dict[int, int]
        self.callback_on_online = callback_on_online  # type: tp.Callable
        self.callback_on_offline = callback_on_offline  # type: tp.Callable
        self.consecutive_failures_to_offline = consecutive_failures_to_offline  # type: int
        self.consecutive_successes_to_online = consecutive_successes_to_online  # type: int

    def _handle(self, success: bool, address: int = 0, *args, **labels):
        if self.embedded_submetrics_enabled or labels:
            return super()._handle(success, address=address, *args, **labels)
        if success:
            self.consecutive_failures[address] = 0
            self.consecutive_successes[address] += 1
            if not self.working[address]:
                if self.consecutive_successes[address] == self.consecutive_successes_to_online:
                    self.working[address] = True
                    self.callback_on_online(address, self.labels)
        else:
            self.consecutive_failures[address] += 1
            self.consecutive_successes[address] = 0

            if self.working[address]:
                if self.consecutive_failures[address] == self.consecutive_failures_to_offline:
                    self.working[address] = False
                    self.callback_on_offline(address, self.labels)

    def to_metric_data(self) -> MetricDataCollection:
        mdc = MetricDataCollection()
        keys = set(self.consecutive_successes.keys())
        keys = keys.union(set(self.consecutive_failures.keys()))
        for address in keys:
            labels = self.labels.copy()
            if keys != {0}:
                labels.update(address=address)
            mdc += MetricData(self.name + '.consecutive_failures',
                              self.consecutive_failures[address],
                              labels, self.get_timestamp(), self.internal)
            mdc += MetricData(self.name + '.consecutive_successes',
                              self.consecutive_successes[address],
                              labels, self.get_timestamp(), self.internal)
            mdc += MetricData(self.name + '.status', int(self.working[address]),
                              self.labels, self.get_timestamp(), self.internal)
        return mdc
