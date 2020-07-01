import http.server
import io
import typing as tp

from satella.coding.concurrent import TerminableThread
from .. import getMetric
from ..data import MetricData, MetricDataCollection

__all__ = ['metric_data_collection_to_prometheus', 'PrometheusHTTPExporterThread']


class PrometheusHandler(http.server.BaseHTTPRequestHandler):
    """A request handler for the PrometheusHTTPExporterThread HTTP server"""

    def do_GET(self):
        """only GETs are supported"""
        if self.path != '/metrics':
            self.send_error(404, 'Unknown path. Only /metrics is supported.')
            return

        metric_data = getMetric().to_metric_data()
        metric_data.add_labels(self.server.extra_labels)
        metric_data = metric_data_collection_to_prometheus(metric_data)
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(metric_data.encode('utf8'))
        self.server.metric.runtime()


class PrometheusHTTPExporterThread(TerminableThread):
    """
    A daemon thread that listens on given interface as a HTTP server, ready to serve as a connection
    point for Prometheus to scrape metrics off this service.

    This additionally (if user requests so) may export a metric called prometheus.exports_per_time
    which is a cps with time_unit_vectors=[1, 20, 60] counting the amount of exports in given time
    period.

    :param interface: a interface to bind to
    :param port: a port to bind to
    :param extra_labels: extra labels to add to each metric data point, such as the name of the
        service or the hostname
    :param enable_metric: whether to enable the metric
    """

    def __init__(self, interface: str, port: int, extra_labels: tp.Optional[dict] = None,
                 enable_metric: bool = False):
        super().__init__(daemon=True)
        self.interface = interface  # type: str
        self.port = port  # type: int
        self.httpd = http.server.HTTPServer((self.interface, self.port), PrometheusHandler,
                                            bind_and_activate=False)
        self.httpd.extra_labels = extra_labels or {}
        self.httpd.metric = getMetric('prometheus.exports_per_time',
                                      'cps' if enable_metric else 'empty',
                                      time_unit_vector=[1, 20, 60])

    def run(self) -> None:
        self.httpd.server_bind()
        self.httpd.server_activate()
        self.httpd.serve_forever()
        self.httpd.server_close()

    def terminate(self, force: bool = False) -> 'PrometheusHTTPExporterThread':
        """
        Order this thread to terminate and return self.

        You will need to .join() on this thread to ensure that it has quit.

        :param force: whether to terminate this thread by injecting an exception into it
        """
        self.httpd.shutdown()
        return super().terminate(force=force)


class RendererObject(io.StringIO):

    def render(self, md: MetricData):

        if md.internal:  # Don't output internal metrics
            return

        self.write(md.name.replace('.', '_'))
        if md.labels:
            self.write('{')
            self.write(','.join('%s="%s"' % (
                key, str(value).replace('\\', '\\\\').replace('"', '\\"')) for
                                key, value in md.labels.items()))
            self.write('}')
        self.write(' %s' % (md.value,))
        if md.timestamp is not None:
            self.write(' %s' % (int(md.timestamp * 1000),))
        self.write('\n')


def metric_data_collection_to_prometheus(mdc: MetricDataCollection) -> str:
    """
    Render the data in the form understandable by Prometheus.

    Values marked as internal will be skipped.

    :param mdc: Metric data collection to render
    :param tree: MetricDataCollection returned by the root metric (or any metric for that instance).
    :return: a string output to present to Prometheus
    """
    if not mdc.values:
        return '\n'
    obj = RendererObject()
    for value in mdc.values:
        if value.internal:
            continue
        obj.render(value)
    return obj.getvalue()
