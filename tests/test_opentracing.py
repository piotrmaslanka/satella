import unittest

from satella.opentracing import trace_exception
from unittest import mock


class TestOpentracing(unittest.TestCase):
    def test_trace_exception_none(self):
        trace_exception(None)

        span = mock.Mock()
        try:
            raise ValueError()
        except ValueError:
            trace_exception(span)

        span.set_tag.assert_called_with('error', True)
        span.log_kv.assert_called()
