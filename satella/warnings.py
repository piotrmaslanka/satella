import warnings

__all__ = ['ExperimentalWarning', 'warnings', 'mark_temporarily_disabled']


class ExperimentalWarning(FutureWarning):
    """
    This feature is experimental!
    """


def mark_temporarily_disabled(reason: str = ''):
    """
    A decorator to mark a function unusable due to some forthcoming changes.

    A call to the function will raise NotImplementedError

    and a mention of this function in code will mark a function disabled for whatever reason.

    Usage:

    >>> @mark_temporarily_disabled('Due to analysis schema changes')
    >>> def serialize_report(analysis):
    >>>     ...
    """

    def outer(fun):
        def inner(*args, **kwargs):
            """
            Function temporarily disabled. Don't call it.
            """
            raise NotImplementedError(f'Function disabled due to {reason}')

        warnings.warn(f'Function {fun.__name__} temporarily disabled due to {reason}')
        return inner

    return outer
