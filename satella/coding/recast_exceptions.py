# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging
import functools

logger = logging.getLogger(__name__)

__all__ = [
    'silence',
    'rethrow_as'
]


def silence_excs(*exc_types):
    return rethrow_as(*[(t, None) for t in exc_types])


class rethrow_as(object):
    """Decorator + context manager"""

    def __init__(self, *pairs, **kwargs):
        self.to_catch = tuple(p[0] for p in pairs)
        self.pairs = pairs
        self.exception_preprocessor = kwargs.get('exception_preprocessor', repr)

    def __call__(self, fun):
        @functools.wraps(fun)
        def inner(*args, **kwargs):
            with self:
                return fun(*args, **kwargs)
        return inner

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        if not isinstance(exc_val, self.to_catch):
            return

        for from_, to in self.pairs:
            if isinstance(exc_val, from_):
                if to is None:
                    return True
                else:
                    raise to(self.exception_preprocessor(exc_val))
