try:
    from cassandra.cluster import ResponseFuture
except ImportError:
    class ResponseFuture:           # pylint: disable=too-few-public-methods
        pass
