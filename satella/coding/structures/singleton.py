import functools

__all__ = [
    'Singleton',
]


# Taken from https://wiki.python.org/moin/PythonDecoratorLibrary
def Singleton(cls):
    """
    Make a singleton out of decorated class.

    Usage:

    >>> @Singleton
    >>> class MyClass(object):
    >>>     ...
    """

    cls.__new_old__ = cls.__new__

    @functools.wraps(cls.__new__)
    def singleton_new(cls, *args, **kw):
        it = cls.__dict__.get('__it__')
        if it is not None:
            return it

        cls.__it__ = it = cls.__new_old__(cls, *args, **kw)
        it.__init_old__(*args, **kw)
        return it

    cls.__new__ = singleton_new
    cls.__init_old__ = cls.__init__
    cls.__init__ = object.__init__

    return cls
