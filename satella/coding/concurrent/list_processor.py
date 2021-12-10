import typing as tp
from concurrent.futures.thread import ThreadPoolExecutor

from satella.coding.typing import V, U

try:
    import opentracing
except ImportError:
    opentracing = None


def parallel_construct(iterable: tp.Iterable[V],
                       function: tp.Callable[[V], tp.Optional[U]],
                       thread_pool: ThreadPoolExecutor) -> tp.List[U]:
    """
    Construct a list from executing given function in a thread pool executor.

    If opentracing is installed, and tracing is enabled, current span will be passed to child threads.

    :param iterable: iterable to apply
    :param function: function to apply. If that function returns None, no element will be added
    :param thread_pool: thread pool to execute
    :return: list that is the result of parallel application of function on each element
    """
    wrap_iterable = None

    if opentracing is not None:
        tracer = opentracing.global_tracer()
        span = tracer.active_span
        if span is not None:
            current_span = tracer.active_span

            def wrap_iterable(arg, *args,  **kwargs):
                tracer.scope_manager.activate(current_span, finish_on_close=False)
                return function(arg, *args, **kwargs)

    if wrap_iterable is None:
        wrap_iterable = function

    result = []
    for item in thread_pool.map(wrap_iterable, iterable):
        if item is not None:
            result.append(item)
    return result
