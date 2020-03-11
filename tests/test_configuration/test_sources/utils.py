import os
import typing as tp
import unittest

from satella.coding import wraps
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
        @wraps(fun)
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
        self.assertEqual(source.provide(), {})

    def assertSourceHas(self, source: BaseSource, value: tp.Any, postop=lambda x: x):
        self.assertEqual(postop(source.provide()), value)
