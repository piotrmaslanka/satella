from satella.coding.decorators import wraps


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

    Note that it will accept any parameters, and then throw them on the ground.
    """

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


def wrap_callable_in_context_manager(clbl, ctxt_mgr, *my_args, **my_kwargs):
    """
    Wrap a callable in context manager.

    Roughly equivalent to:

    >>> def inner(*args, **kwargs):
    >>>     with ctxt_mgr(*my_args, **my_kwargs):
    >>>         return clbl(*args, **kwargs)
    >>> return inner

    To be used as:

    >>> clbl = wrap_callable_in_context_manager(lambda y: 5, tracing.start_new_span, 'New span')
    """
    @wraps(clbl)
    def inner(*args, **kwargs):
        with ctxt_mgr(*my_args, **my_kwargs):
            return clbl(*args, **kwargs)
    return inner
