try:
    from cassandra.cluster import ResponseFuture
except ImportError:
    class ResponseFuture:
        pass
