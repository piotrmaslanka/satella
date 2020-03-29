from satella.configuration.sources import MergingSource, JSONSource, \
    AlternativeSource, StaticSource
from satella.exceptions import ConfigurationError
from .utils import SourceTestCase


class TestMergingSource(SourceTestCase):
    def test_ok(self):
        s = MergingSource(
            JSONSource('{"a": [5]}'),
            JSONSource('{"a": [6]}'),
        )
        self.assertSourceHas(s, {"a": [5, 6]})

    def test_fails_on_none(self):
        s = MergingSource(
            JSONSource('{"a: [5]}'),
            on_fail=MergingSource.SILENT,
            fail_if_no_sources_are_correct=True
        )
        self.assertRaises(ConfigurationError, s.provide)

        s = MergingSource(
            JSONSource('{"a: [5]}'),
            on_fail=MergingSource.SILENT,
            fail_if_no_sources_are_correct=False
        )
        self.assertEqual(s.provide(), {})

    def test_empty(self):
        self.assertSourceEmpty(MergingSource())

    def test_static(self):
        st = StaticSource({'a': 5})
        self.assertEqual(st.provide(), {'a': 5})


class TestAlternativeSource(SourceTestCase):
    def test_alternative(self):
        self.assertSourceFails(AlternativeSource(), ConfigurationError)
