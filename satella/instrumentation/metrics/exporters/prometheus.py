import logging
import io
from satella.coding.concurrent import TerminableThread
import http.server
from .. import getMetric
from ..data import MetricData, MetricDataCollection

logger = logging.getLogger(__name__)

__all__ = ['metric_data_collection_to_prometheus', 'PrometheusHTTPExporterThread']


class PrometheusHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path != '/metrics':
            self.send_error(404, 'Unknown path. Only /metrics is supported.')
            return

        root_metric = getMetric()

        metric_data = metric_data_collection_to_prometheus(root_metric.to_metric_data())
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(metric_data.encode('utf8'))


class PrometheusHTTPExporterThread(TerminableThread):
    """
    A daemon thread that listens on given interface as a HTTP server, ready to serve as a connection
    point for Prometheus to scrape metrics off this service.

    :param interface: a interface to bind to
    :param port: a port to bind to
    """
    def __init__(self, interface: str, port: int):
        super().__init__(daemon=True)
        self.interface = interface
        self.port = port
        self.httpd = http.server.HTTPServer((self.interface, self.port), PrometheusHandler,
                                            bind_and_activate=False)

    def run(self):
        self.httpd.server_bind()
        self.httpd.server_activate()
        self.httpd.serve_forever()
        self.httpd.server_close()

    def terminate(self, force: bool = False):
        self.httpd.shutdown()
        return super().terminate(force=force)


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
    Render the data in the form understandable by Prometheus

    :param tree: MetricDataCollection returned by the root metric (or any metric for that instance).
    :return: a string output to present to Prometheus
    """
    if not mdc.values:
        return '\n'
    obj = RendererObject()
    for value in mdc.values:
        obj.render(value)
    return obj.getvalue()
