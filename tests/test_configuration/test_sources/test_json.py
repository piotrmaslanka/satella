import unittest

from satella.configuration.sources import JSONSource, OptionalSource, \
    FORMAT_SOURCES
from .utils import SourceTestCase


class TestJSONSource(SourceTestCase):
    @unittest.skipIf('TOMLSource' not in FORMAT_SOURCES, 'No TOML installed')
    def test_toml(self):
        from satella.configuration.sources import TOMLSource
        self.assertSourceHas(TOMLSource(u"key = 5"), {"key": 5})
        self.assertSourceFails(TOMLSource(u'this isnt toml'))

    @unittest.skipIf('YAMLSource' not in FORMAT_SOURCES, 'No YAML installed')
    def test_yaml(self):
        from satella.configuration.sources import YAMLSource
        self.assertSourceHas(YAMLSource(u"\na: 5\n"), {"a": 5})
        self.assertSourceFails(
            YAMLSource(u'!3 #23= 43$ 434 #34 = this isnt yaml'))

    def test_ok(self):
        self.assertSourceHas(JSONSource(u'{"a":2}'), {"a": 2})

    def test_malform(self):
        self.assertSourceFails(JSONSource(u'sdfsf>>::'))
        self.assertSourceEmpty(OptionalSource(JSONSource(u'sdfsf>>::')))

    def test_base64_bad(self):
        self.assertSourceFails(JSONSource(b'bG9s\x02', encoding='base64'))

    def test_unicode_bad(self):
        self.assertSourceFails(JSONSource(b'\x00'))
