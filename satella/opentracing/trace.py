import typing as tp
from concurrent.futures import Future

from satella.coding.decorators import wraps

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


def trace_function(tracer, name: str, tags: tp.Optional[dict] = None):
    """
    Return a decorator that will trace the execution of a given function
    using tracer.start_active_span

    :param tracer: tracer to use
    :param name: Name of the trace
    :param tags: optional tags to use
    """
    def outer(fun):
        @wraps(fun)
        def inner(*args, **kwargs):
            with tracer.start_active_span(name, tags=tags):
                return fun(*args, **kwargs)
        return inner
    return outer


def trace_future(future: tp.Union[ResponseFuture, Future], span: Span):
    """
    Install a handler that will close a span upon a future completing,
    attaching the exception contents if the future ends with an exception.

    :param future: can be either a normal Future or a Cassandra's ResponseFuture
    :param span: span to close on future's completion
    """
    if isinstance(future, ResponseFuture):
        def close_exception(exc):
            # noinspection PyProtectedMember
            Span._on_error(span, type(exc), exc, '<unavailable>')
            span.finish()

        future.add_callback(span.finish)
        future.add_errback(close_exception)
    else:
        def close_future(fut):
            exc = fut.exception()
            if exc is not None:
                # noinspection PyProtectedMember
                Span._on_error(span, type(exc), exc, '<unavailable>')
            span.finish()
        future.add_done_callback(close_future)
