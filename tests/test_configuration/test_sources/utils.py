import functools
import os
import unittest
import typing as tp

from satella.configuration.sources import BaseSource
from satella.exceptions import ConfigurationError


def mock_env(env: tp.Optional[str] = None, val: tp.Optional[str] = None) -> \
        tp.Callable[[tp.Callable], tp.Callable]:
    """
    Set an env and then clear it out
    :param env:
    :param val:
    :return:
    """

    def outer(fun: tp.Callable):
        @functools.wraps(fun)
        def inner(*args, **kwargs):
            try:
                if env is not None:
                    os.environ[env] = val
                return fun(*args, **kwargs)
            finally:
                if env is not None:
                    del os.environ[env]

        return inner

    return outer


class SourceTestCase(unittest.TestCase):
    def assertSourceFails(self, source: BaseSource,
                          fails_with=ConfigurationError):
        self.assertRaises(fails_with, source.provide)

    def assertSourceEmpty(self, source: BaseSource):
        self.assertEqual(self.provide(source), {})

    def assertSourceHas(self, source: BaseSource, value: tp.Any, postop=lambda x: x):
        self.assertEqual(postop(self.provide(source)), value)

    def provide(self, source: BaseSource) -> dict:
        return source.provide()
