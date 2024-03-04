import inspect
import logging

logger = logging.getLogger(__name__)


class transaction:
    """
    A context manager for wrapping a transaction and getting a cursor from the Python DB API 2.

    Use it as a context manager. commit and rollback will be automatically called for you.

    Use like:

    >>> with transaction(conn) as cur:
    >>>   cur.execute('DROP DATABASE')

    Leaving the context manager will automatically close the cursor for you.

    :param connection_or_getter: the connection object to use, or a callable, that called with
        zero arguments will provide us with a connection
    :param close_the_connection_after: whether the connection should be closed after use
    :param log_exception: whether to log an exception if it happens
    """

    def __init__(self, connection_or_getter, close_the_connection_after: bool = False,
                 log_exception: bool = True):
        self._connection = connection_or_getter
        self.close_the_connection_after = close_the_connection_after
        self.cursor = None
        self.log_exception = log_exception

    def __enter__(self):
        self.cursor = self.connection.cursor()
        return self.cursor

    @property
    def connection(self):
        if inspect.isfunction(self._connection):
            conn = self._connection()
            self._connection = conn
            return conn
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
