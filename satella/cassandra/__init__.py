import itertools
import typing as tp
from collections import namedtuple


def parallel_for(cursor, query: tp.Union[tp.List[str], str, 'Statement', tp.List['Statement']],
                 arguments: tp.Iterable[tuple]) -> tp.Iterator[namedtuple]:
    """
    Syntactic sugar for

    >>> futures = []
    >>> for args in arguments:
    >>>     futures.append(cursor.execute_async(query, args))
    >>> for future in futures:
    >>>     yield future.result()

    If query is a string, or else

    >>> futures = []
    >>> for query, args in zip(query, arguments):
    >>>     futures.append(cursor.execute_async(query, args))
    >>> for future in futures:
    >>>     yield future.result()

    :param cursor: the Cassandra cursor to use (obtained using connection.session())
    :param query: base query or a list of queries, if a different one is to be used
    :param arguments: iterable yielding arguments to use in execute_async
    """
    from cassandra.query import Statement

    if isinstance(query, (str, Statement)):
        query = itertools.repeat(query)

    futures = [cursor.execute_async(query, args) for query, args in zip(query, arguments)]

    for future in futures:
        yield future.result()
