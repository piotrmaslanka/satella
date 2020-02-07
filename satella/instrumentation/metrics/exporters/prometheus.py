import logging
import io
import copy
from satella.coding import for_argument

from ..data import MetricData, MetricDataCollection

logger = logging.getLogger(__name__)

__all__ = ['metric_data_collection_to_prometheus']


class RendererObject(io.StringIO):

    def render(self, md: MetricData):
        self.write(md.name.replace('.', '_'))
        if md.labels:
            self.write('{')
            self.write(','.join('%s="%s"' % (key, value) for key, value in md.labels.items()))
            self.write('}')
        self.write(' %s' % (md.value, ))
        if md.timestamp is not None:
            self.write(' %s' % (int(md.timestamp*1000), ))
        self.write('\n')


def metric_data_collection_to_prometheus(mdc: MetricDataCollection) -> str:
    """
    Render the JSON in the form understandable by Prometheus

    :param tree: JSON returned by the root metric (or any metric for that instance).
    :return: a string output to present to Prometheus
    """
    if not mdc.values:
        return '\n'
    obj = RendererObject()
    for value in mdc.values:
        obj.render(value)
    return obj.getvalue()
