import unittest

from satella.coding.concurrent import call_in_separate_thread
from satella.opentracing import trace_exception, trace_future
from unittest import mock


class TestOpentracing(unittest.TestCase):
    def test_trace_future(self):
        @call_in_separate_thread()
        def test_me():
            pass

        fut = test_me()
        span = mock.Mock()
        trace_future(fut, span)
        fut.result()
        fut.thread.join()
        span.finish.assert_called()

    def test_trace_exception_none(self):
        trace_exception(None)

        span = mock.Mock()
        try:
            raise ValueError()
        except ValueError:
            trace_exception(span)

        span.set_tag.assert_called_with('error', True)
        span.log_kv.assert_called()
