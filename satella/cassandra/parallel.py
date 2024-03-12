import itertools
import typing as tp
import warnings
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

    .. deprecated:: 2.14.22
        Use Cassandra_ feature for that

    .. _Cassandra: https://docs.datastax.com/en/developer/python-driver/3.24/api/cassandra/concurrent/

    :param cursor: the Cassandra cursor to use (obtained using connection.session())
    :param query: base query or a list of queries, if a different one is to be used
    :param arguments: iterable yielding arguments to use in execute_async
    """
    warnings.warn('This is deprecated and will be removed in Satella 3.0', DeprecationWarning)
    try:
        from cassandra.query import Statement       # pylint: disable=import-outside-toplevel
        query_classes = (str, Statement)
    except ImportError:
        query_classes = str

    if isinstance(query, query_classes):
        query = itertools.repeat(query)

    futures = []
    for loc_query, args in zip(query, arguments):
        future = cursor.execute_async(loc_query) if args is None else cursor.execute_async(loc_query, args)
        futures.append(future)

    for future in futures:
        yield future.result()
