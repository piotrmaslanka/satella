import typing as tp
from concurrent.futures import Future
try:
    from opentracing import Span
except ImportError:
    class Span:
        pass

try:
    from cassandra.cluster import ResponseFuture
except ImportError:
    class ResponseFuture:
        pass


def trace_future(future: tp.Union[ResponseFuture, Future], span: Span):
    """
    Install a handler that will close a span upon a future completing,
    attaching the exception contents if the future ends with an exception.

    :param future: can be either a normal Future or a Cassandra's ResponseFuture
    :param span: span to close on future's completion
    """
    if isinstance(future, ResponseFuture):
        def close_exception(exc):
            Span._on_error(span, type(exc), exc, '<unavailable>')
            span.finish()

        future.add_callback(span.finish)
        future.add_errback(close_exception)
    else:
        def close_future(fut):
            exc = fut.exception()
            if exc is not None:
                Span._on_error(span, type(exc), exc, '<unavailable>')
            span.finish()
        future.add_done_callback(close_future)
