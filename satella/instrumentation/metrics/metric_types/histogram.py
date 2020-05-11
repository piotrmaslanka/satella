import math
import typing as tp
import itertools
from .base import EmbeddedSubmetrics, MetricLevel
from .measurable_mixin import MeasurableMixin
from .registry import register_metric
from ..data import MetricData, MetricDataCollection, MetricDataContainer


@register_metric
class HistogramMetric(EmbeddedSubmetrics, MeasurableMixin):
    """
    A histogram, by  `Prometheus' <https://github.com/prometheus/client_python#histogram/>`_
    interpretation.
    
    :param buckets: buckets to add. First bucket will be from zero to first value, second from first
        value to second, last bucket will be from last value to infinity. So there are 
        len(buckets)+1 buckets. Buckets are expected to be passed in sorted!
    :param aggregate_children: whether to accept child calls to be later presented as total
    """
    __slots__ = ('bucket_limits', 'buckets', 'aggregate_children', 'count', 'sum')

    CLASS_NAME = 'histogram'

    def __init__(self, name: str, root_metric: 'Metric' = None,
                 metric_level: tp.Optional[MetricLevel] = None,
                 internal: bool = False,
                 buckets: tp.Sequence[float] = (.005, .01, .025, .05, .075, .1, .25, .5,
                                                .75, 1.0, 2.5, 5.0, 7.5, 10.0),
                 aggregate_children: bool = True, *args, **kwargs):
        super().__init__(name, root_metric, metric_level, internal=internal, buckets=buckets,
                         aggregate_children=aggregate_children, metric_type='histogram', *args, **kwargs)
        self.bucket_limits = list(buckets)                   # type: tp.List[float]
        self.buckets = [0] * (len(buckets) + 1)              # type: tp.List[int]
        self.aggregate_children = aggregate_children         # type: bool
        self.count = 0                                       # type: int
        self.sum = 0.0                                       # type: float

    def _handle(self, value, **labels):
        self.count += 1
        self.sum += value

        if self.embedded_submetrics_enabled or labels:
            super()._handle(value, **labels)

            if not self.aggregate_children:
                return

        lower_bound = 0.0
        for index, upper_bound in itertools.chain(enumerate(self.bucket_limits),
                                                  [(len(self.bucket_limits), math.inf)]):
            if lower_bound <= value < upper_bound:
                self.buckets[index] += 1
            lower_bound = upper_bound

    def to_metric_data_container(self) -> MetricDataContainer:
        if self.embedded_submetrics_enabled:
            k = super().to_metric_data_container()
            if self.aggregate_children:
                mdc = self.containers_to_metric_data()
                for entry in mdc:
                    entry.postfix_with('bucket')
                    mdc += entry

                mdc += MetricData(self.name+'.sum', self.sum, {})
                mdc += MetricData(self.name+'.count', self.count, {})
                k += mdc
            return k
        else:
            mdc = super().to_metric_data_container()
            for entry in self.containers_to_metric_data():
                entry.postfix_with('bucket')
                mdc += entry

            mdc += MetricData(self.name+'.sum', self.sum, self.labels)
            mdc += MetricData(self.name+'.count', self.count, self.labels)
            return mdc

    def containers_to_metric_data(self) -> tp.List[MetricData]:
        output = []
        lower_bound = 0.0
        for amount, upper_bound in zip(self.buckets,
                                       self.bucket_limits + [math.inf]):
            labels = self.labels.copy()
            labels.update(le=upper_bound,
                          ge=lower_bound)
            output.append(MetricData(self.name, amount, labels))
            lower_bound = upper_bound
        return output
