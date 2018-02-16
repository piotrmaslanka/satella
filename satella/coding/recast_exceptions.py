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
    """
    Silence given exception types.

    Can be either a decorator or a context manager
    """
    return rethrow_as(*[(t, None) for t in exc_types])


class rethrow_as(object):
    """
    Transform some exceptions into others.

    Either a decorator or a context manager
    """


    def __init__(self, *pairs, **kwargs):
        """
        Pass tuples of (exception to catch - exception to transform to).

        New exception will be created by calling exception to transform to with
        repr of current one.

        You can also provide just two exceptions, eg.

          rethrow_as(NameError, ValueError)

        :param exception_preprocessor: other callable/1 to use instead od repr.
            Should return a text
        """

        # You can also provide just two exceptions
        if len(pairs) == 2 and not isinstance(pairs[1], (tuple, list)) \
                and all(issubclass(p, BaseException) for p in pairs):
            self.mapping = {pairs[0]: pairs[1]}
        else:
            self.mapping = dict(pairs)

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
        if exc_type not in self.mapping:
            return

        fate = self.mapping[exc_type]

        if fate is None:    # mask it
            return True
        else:
            raise fate(self.exception_preprocessor(exc_val))
