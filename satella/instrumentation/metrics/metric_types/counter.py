import logging
import typing as tp
from .base import EmbeddedSubmetrics, LeafMetric
from .registry import register_metric
logger = logging.getLogger(__name__)


@register_metric
class CounterMetric(EmbeddedSubmetrics):
    """
    A counter that can be adjusted by a given value.

    :param sum_children: whether to sum up all calls to children
    :param count_calls: count the amount of calls to handle()
    """
    CLASS_NAME = 'counter'

    def __init__(self, name, root_metric: 'Metric' = None, metric_level: str = None,
                 sum_children: bool = True,
                 count_calls: bool = False, *args, **kwargs):
        super().__init__(name, root_metric, metric_level, sum_children=sum_children,
                         count_calls=count_calls, *args, **kwargs)
        self.sum_children = sum_children
        self.count_calls = count_calls
        self.calls = 0
        self.value = 0

    def to_json(self) -> list:
        if self.embedded_submetrics_enabled:
            k = super().to_json()
            if self.sum_children:
                r = LeafMetric.to_json(self)
                r['_'] = self.value
                k = {'_': k, 'sum': r}
                if self.count_calls:
                    q = LeafMetric.to_json(self)
                    q['_'] = self.calls
                    k['count'] = q
            return k

        p = super().to_json()
        p['_'] = self.value
        if self.count_calls:
            r, q = super().to_json(), super().to_json()
            r['_'] = self.value
            p['_'] = r
            q['_'] = self.calls
            p['count'] = q
        return p

    def _handle(self, delta: float = 0, **labels):
        if self.embedded_submetrics_enabled or labels:
            if self.sum_children:
                self.value += delta
            self.calls += 1
            return super()._handle(delta, **labels)

        self.value += delta
        self.calls += 1
