from concurrent.futures import Future

from .common import ResponseFuture


def wrap_future(future: ResponseFuture) -> Future:
    """
    Convert a Cassandra's future to a normal Python future.
    The returned future will be marked as running.

    future is returned when it's already a Python future.

    :param future: cassandra future to wrap
    :return: a standard Python future
    """
    if isinstance(future, Future):
        return future

    fut = Future()
    fut.set_running_or_notify_cancel()
    future.add_callback(fut.set_result)
    future.add_errback(fut.set_exception)
    return fut
