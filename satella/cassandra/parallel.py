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

    If query is a string or a Cassandra Statement, or else

    >>> futures = []
    >>> for query, args in zip(query, arguments):
    >>>     futures.append(cursor.execute_async(query, args))
    >>> for future in futures:
    >>>     yield future.result()

    Note that if None is encountered in the argument iterable, session.execute() will
    be called with a single argument. You better have it as a BoundStatement then!

    :param cursor: the Cassandra cursor to use (obtained using connection.session())
    :param query: base query or a list of queries, if a different one is to be used
    :param arguments: iterable yielding arguments to use in execute_async
    """
    try:
        from cassandra.query import Statement
        query_classes = (str, Statement)
    except ImportError:
        query_classes = str

    if isinstance(query, query_classes):
        query = itertools.repeat(query)

    futures = []
    for query, args in zip(query, arguments):
        if args is None:
            future = cursor.execute_async(query)
        else:
            future = cursor.execute_async(query, args)
        futures.append(future)

    for future in futures:
        yield future.result()
