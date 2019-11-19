import logging
import typing
import functools

logger = logging.getLogger(__name__)


def static_var(var_name, value):
    def decorate(func):
        setattr(func, var_name, value)
        return func
    return decorate