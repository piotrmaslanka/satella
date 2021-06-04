import copy
import sys
import typing as tp
import warnings
from concurrent.futures import Future

from satella.coding.decorators import wraps
from ..cassandra.common import ResponseFuture
from ..cassandra.future import wrap_future

try:
    from opentracing import Span
except ImportError:
    class Span:
        @classmethod
        def _on_error(cls, span, exc_type, value, traceback):
            pass


def trace_function(tracer, name: str, tags: tp.Optional[dict] = None,
                   tags_factory: tp.Optional[tp.Union[
                       tp.Dict[str, tp.Callable], tp.List[tp.Tuple[str, tp.Callable]]]] = None):
    """
    Return a decorator that will trace the execution of a given function
    using tracer.start_active_span.

    Can optionally construct it's tags from a predicate building, example:

    >>> class Device:
    >>>     device_id = 'test'
    >>> @trace_function(tracer, 'Processing', tags_factory=[('device_id', x[0].device_id)])
    >>> def process(device: Device):
    >>>     ...

    :param tracer: tracer to use
    :param name: Name of the trace
    :param tags: optional tags to use
    :param tags_factory: a list of tuple (tag name, callable that is called with *args
        and **kwargs passed to this function as a sole argument). Extra tags will be generated
        from this. Can be also a dict.
    """
    if isinstance(tags_factory, dict):
        tags_factory = list(tags_factory.items())

    def outer(fun):
        @wraps(fun)
        def inner(*args, **kwargs):
            nonlocal tags, tags_factory
            my_tags = tags
            if tags_factory is not None:
                if tags is None:
                    tags = {}
                my_tags = copy.copy(tags)
                for key, value in tags_factory:
                    try:
                        v = value(*args, **kwargs)
                    except TypeError:
                        warnings.warn('You are using the deprecated single-parameter version '
                                      'of tags_factory. Please upgrade to the newer one.',
                                      DeprecationWarning)
                        v = value(args)
                    my_tags[key] = v
            with tracer.start_active_span(name, tags=my_tags):
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
        warnings.warn('Tracing Cassandra futures is deprecated. Use wrap_future() to '
                      'convert it to a standard Python future. This feature will be '
                      'deprecated in Satella 3.x', DeprecationWarning)
        future = wrap_future(future)

    def close_future(fut):
        exc = fut.exception()
        if exc is not None:
            # noinspection PyProtectedMember
            exc_type, value, traceback = sys.exc_info()
            Span._on_error(span, exc_type, value, traceback)
        span.finish()

    future.add_done_callback(close_future)
