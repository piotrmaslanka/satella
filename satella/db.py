import inspect
import logging

from satella.coding import wraps

logger = logging.getLogger(__name__)


class transaction:
    """
    A context manager for wrapping a transaction and getting a cursor from the Python DB API 2.

    Use it as a context manager. commit and rollback will be automatically called for you.

    Use like:

    >>> with transaction(conn) as cur:
    >>>   cur.execute('DROP DATABASE')

    Leaving the context manager will automatically close the cursor for you.

    >>> def conn_getter_function() -> connection:
    >>>     ....
    >>> @transaction(conn_getter_function)
    >>>     ....

    The same syntax can be used, if you session depends eg. on a thread.

    :param connection_or_getter: the connection object to use, or a callable/0, that called with
        this thread will provide us with a connection
    :param close_the_connection_after: whether the connection should be closed after use, False by default
    :param log_exception: whether to log an exception if it happens
    """
    def __init__(self, connection_or_getter, close_the_connection_after: bool = False,
                 log_exception: bool = True):
        self._connection = connection_or_getter
        self.close_the_connection_after = close_the_connection_after
        self.cursor = None
        self.log_exception = log_exception

    def __call__(self, fun):
        @wraps(fun)
        def inner(*args, **kwargs):
            with self as cur:
                if fun.__name__ == fun.__qualname__:
                    return fun(cur, *args, **kwargs)
                else:
                    if not len(args):
                        return fun(*args)
                    else:
                        return fun(*args[0], cur, *args[1:], **kwargs)
        return inner

    def __enter__(self):
        self.cursor = self.connection.cursor()
        return self.cursor

    @property
    def connection(self):
        if inspect.isfunction(self._connection):
            return self._connection()
        else:
            return self._connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            self.connection.commit()
        else:
            self.connection.rollback()

        if exc_val is not None and self.log_exception:
            logger.error('Exception occurred of type %s', exc_type, exc_info=exc_val)

        self.cursor.close()

        if self.close_the_connection_after:
            self.connection.close()

        return False
