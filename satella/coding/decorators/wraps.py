import inspect
import typing as tp

def wraps(cls_to_wrap: tp.Type) -> tp.Callable[[tp.Type], tp.Type]:
    """
    A functools.wraps() but for classes.

    As a matter of fact, this can replace functools.wraps() entirely.
    This replaces __doc__, __name__, __module__ and __annotations__.
    It also sets a correct __wrapped__.

    :param cls_to_wrap: class to wrap
    """

    def outer(cls: tp.Type) -> tp.Type:
        if hasattr(cls_to_wrap, '__doc__'):
            try:
                cls.__doc__ = cls_to_wrap.__doc__
            except AttributeError:
                pass
        if hasattr(cls_to_wrap, '__name__'):
            try:
                cls.__name__ = cls_to_wrap.__name__
            except (AttributeError, TypeError):
                pass
        if hasattr(cls_to_wrap, '__module__'):
            try:
                cls.__module__ = cls_to_wrap.__module__
            except AttributeError:
                pass
        if hasattr(cls_to_wrap, '__annotations__'):
            try:
                cls.__annotations__ = cls_to_wrap.__annotations__
            except (AttributeError, TypeError):
                pass
        try:
            sig = inspect.signature(cls_to_wrap)
            cls.__signature__ = sig
        except (TypeError, ValueError, RecursionError, AttributeError):
            pass
        try:
            cls.__wrapped__ = cls_to_wrap
        except AttributeError:
            pass
        return cls

    return outer
