import logging
import typing
import functools

logger = logging.getLogger(__name__)


def static_var(var_name, value):
    """
    Declare a static variable for given function

    Use it like:

    @static_var('counter', 2)
    def count():
        count.counter += 1

    or:

    class MyClass:
        @static_var('counter', 2)
        def count():
            MyClass.counter += 1
    """
    def decorate(func):
        setattr(func, var_name, value)
        return func
    return decorate
