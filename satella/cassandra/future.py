from concurrent.futures import Future

from .common import ResponseFuture


def wrap_future(future: ResponseFuture) -> Future:
    """
    Convert a Cassandra's future to a normal Python future.
    The future is returned already

    :param future: cassandra future to wrap
    :return: a standard Python future
    :raises TypeError: when a normal Python future is passed as future
    """
    if isinstance(future, Future):
        raise TypeError('Tried to wrap an existing Future!')

    fut = Future()
    fut.set_running_or_notify_cancel()
    future.add_callback(lambda result: fut.set_result(result))
    future.add_errback(lambda exception: fut.set_exception(exception))
    return fut
