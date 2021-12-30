class EmptyContextManager:
    """
    A context manager that does nothing. Only to support conditional change of context managers,
    eg in such a way:

    >>> if tx_enabled:
    >>>     ctxt = transaction.atomic
    >>> else:
    >>>     ctxt = EmptyContextManager()
    >>> with ctxt:
    >>>     ...
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
