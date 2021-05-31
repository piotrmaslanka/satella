import unittest

from satella.opentracing import trace_exception


class TestOpentracing(unittest.TestCase):
    def test_trace_exception_none(self):
        trace_exception(None)
