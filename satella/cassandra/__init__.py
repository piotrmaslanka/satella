import typing as tp
from collections import namedtuple


def parallel_for(cursor, query: str, arguments: tp.Iterable[tuple]) -> tp.Iterator[namedtuple]:
    """
    Syntactic sugar for

    >>> futures = []
    >>> for args in arguments:
    >>>     futures.append(cur.execute_async(query, args))
    >>> for future in futures:
    >>>     yield future.result()

    :param cursor: the Cassandra cursor to use (obtained using connection.session())
    :param query: base query
    :param arguments: iterable yielding arguments to use in execute_async
    """
    futures = []
    for args in arguments:
        futures.append(cursor.execute_async(query, args))

    for future in futures:
        yield future.result()
