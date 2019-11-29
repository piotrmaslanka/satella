from satella.configuration.sources import MergingSource, JSONSource, \
    AlternativeSource
from satella.exceptions import ConfigurationError
from .utils import SourceTestCase


class TestMergingSource(SourceTestCase):
    def test_ok(self):
        s = MergingSource(
            JSONSource('{"a": [5]}'),
            JSONSource('{"a": [6]}'),
        )
        self.assertSourceHas(s, {"a": [5, 6]})

    def test_empty(self):
        self.assertSourceEmpty(MergingSource())


class TestAlternativeSource(SourceTestCase):
    def test_alternative(self):
        self.assertSourceFails(AlternativeSource(), ConfigurationError)
