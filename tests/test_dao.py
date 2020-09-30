import unittest

from satella.dao import Loadable, must_be_loaded


class TestDAO(unittest.TestCase):
    def test_something(self):
        class Load(Loadable):
            def __init__(self, load_lazy=False):
                super().__init__(load_lazy=load_lazy)

            @must_be_loaded
            def method_accessed(self):
                assert self._loaded

            def refresh(self, load_from=None) -> None:
                super().refresh(load_from=load_from)

        l = Load()
        l.method_accessed()
