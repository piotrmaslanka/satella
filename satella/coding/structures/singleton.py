from ..decorators import wraps


# noinspection PyPep8Naming
def Singleton(cls):
    """
    Make a singleton out of decorated class.

    Usage:

    >>> @Singleton
    >>> class MyClass:
    >>>     ...
    """

    cls.__new_old__ = cls.__new__

    @wraps(cls.__new__)
    def singleton_new(cls, *args, **kw):
        it = cls.__dict__.get('__it__')
        if it is not None:
            return it

        cls.__it__ = it = cls.__new_old__(cls)
        it.__init_old__(*args, **kw)
        return it

    cls.__new__ = singleton_new
    cls.__init_old__ = cls.__init__
    cls.__init__ = wraps(cls.__init__)(
        lambda self, *args, **kwargs: object.__init__(self))

    return cls


# noinspection PyPep8Naming
def SingletonWithRegardsTo(num_args: int):
    """
    Make a memoized singletion depending on the arguments.

    A dictionary is made (first N arguments => class instance) and such is returned.
    Please take care to ensure that a tuple made out of first num_args can be used as a dictionary
    key (ie. is both hashable and __eq__-able).

    Usage:

    >>> @SingletonWithRegardsTo(num_args=1)
    >>> class MyClass:
    >>>     def __init__(self, device_id: str):
    >>>         ...
    >>> a = MyClass('dev1')
    >>> b = MyClass('dev2')
    >>> c = MyClass('dev1')
    >>> assert a is c
    >>> assert b is not c
    """

    def inner(cls):

        cls.__new_old__ = cls.__new__

        @wraps(cls.__new__)
        def singleton_new(cls, *args, **kw):
            it = cls.__dict__.get('__it__')
            if it is None:
                it = cls.__it__ = {}

            key = args[:num_args]
            if key in it:
                return it[key]

            inst = it[key] = cls.__new_old__(cls)
            inst.__init_old__(*args, **kw)
            return inst

        cls.__new__ = singleton_new
        cls.__init_old__ = cls.__init__
        cls.__init__ = wraps(cls.__init__)(
            lambda self, *args, **kwargs: object.__init__(self))

        return cls

    return inner
