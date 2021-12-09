import unittest

from satella.coding.concurrent import call_in_separate_thread
from satella.opentracing import trace_exception, trace_future, trace_function, \
    set_maximum_traceback_length
from unittest import mock


class TestOpentracing(unittest.TestCase):
    def test_trace_function(self):
        slf = self

        class MockTracer:
            def __init__(self):
                self.start_active_span_called = True

            def start_active_span(self, *args, tags=None, **kwargs):
                slf.assertEqual(tags, {'a': 'b', 'c': 'd', 'e': 'f'})

                class MockScope(mock.Mock):
                    def __enter__(self):
                        return self

                    def __exit__(self, exc_type, exc_val, exc_tb):
                        return False
                self.start_active_span_called = True
                return MockScope()

        tracer = MockTracer()

        @trace_function(tracer, 'trace_me',
                        tags_factory= {'a': lambda: 'b',
                                       'c': lambda: 'd',
                                       'e': (lambda args: 'f')})
        def trace_me():
            pass

        trace_me()
        self.assertTrue(tracer.start_active_span_called)

    def test_trace_future_success(self):
        @call_in_separate_thread()
        def test_me():
            pass

        fut = test_me()
        span = mock.MagicMock()
        trace_future(fut, span)
        fut.result()
        fut.thread.join()
        self.assertTrue(span.finish.called)

    def test_trace_future_exception(self):
        @call_in_separate_thread()
        def fail_me():
            raise ValueError()

        fut = fail_me()
        span = mock.Mock()
        trace_future(fut, span)
        self.assertRaises(ValueError, fut.result)
        fut.thread.join()
        self.assertTrue(span.finish.called)

    def test_trace_exception_none(self):
        trace_exception(None)
        set_maximum_traceback_length(32768)

        span = mock.MagicMock()
        try:
            raise ValueError()
        except ValueError:
            trace_exception(span)

        self.assertTrue(span.set_tag.called)
        self.assertTrue(span.log_kv.called)
