import typing as tp


def static_var(var_name: str, starting_value: tp.Optional[tp.Any] = None):
    """
    Declare a static variable for given function

    Use it like:

    >>> @static_var('counter', 2)
    >>> def count():
    >>>     count.counter += 1

    or:

    >>> class MyClass:
    >>>     @static_var('counter', 2)
    >>>     def count(self):
    >>>         MyClass.count.counter += 1
    """

    def decorate(func):
        setattr(func, var_name, starting_value)
        return func

    return decorate
