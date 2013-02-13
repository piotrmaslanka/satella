from satella.instrumentation.logging import LogEntry, LogSet, LoggerInterface
# LoggerInterface is implemented only as API check

import unittest

class LogsetTest(unittest.TestCase):
    def test_logset_filtering(self):
        f = [
                LogEntry('x.y.z.a', 'satella test', 1),
                LogEntry('x.y.z', 'satella test', 2),
                LogEntry('x.y.za', 'satella test', 3),
                LogEntry('x.y.b', 'satella notest', 4),
                LogEntry('x.f', 'satella notest', 5),
            ]

        ls = LogSet(f)

        self.assertEquals(ls.count(), 5)
        self.assertEquals(ls.filter_tag('satella').count(), 5)
        self.assertEquals(ls.filter_tag('test').count(), 3)

        self.assertEquals(ls.filter_hierarchy('x.y.z').count(), 2)
        self.assertEquals(ls.filter_hierarchy('x.y').count(), 4)
        self.assertEquals(ls.filter_hierarchy('x').count(), 5)

        self.assertEquals(ls.filter_hierarchy('x.y').filter_tag('notest').count(), 1)

        self.assertEquals(ls.filter_tag(('satella', 'notest')).count(), 2)

        self.assertEquals(ls.filter_when_from(2).count(), 4)
        self.assertEquals(ls.filter_when_to(3).count(), 3)
        self.assertEquals(ls.filter_when_from(2).filter_when_to(4).count(), 3)

        self.assertEquals(len(list(ls.events())), 5)

class LoggingTest(unittest.TestCase):
    def test_attach(self):
        le = LogEntry('satella.instrumentation.unit_tests', ('satella', 'test'))

        le.attach('test string', 'hello world')

        self.assertEquals(len(le.attachments), 1)

    def test_getattr_behaviour(self):
        k = LogEntry('a.b', 'a b').set_data(stefan='nope')
        self.assertEquals(k.stefan, 'nope')

    def test_compact_serialization(self):
        k = LogEntry('a.b', 'a b')              \
                .set_data(stefan='nope')        \
                .attach('stefan', 'nope')

        k = LogEntry.from_compact(k.to_compact())
        self.assertEquals(k.attachments['stefan'], 'nope')
        self.assertEquals(k.data['stefan'], 'nope')

    def test_JSON_serialization(self):
        k = LogEntry('a.b', 'a b').attach('stefan', 'nope').set_data(stefan='nope')

        k = LogEntry.from_JSON(k.to_JSON())

        self.assertEquals(k.attachments['stefan'], 'nope')
        self.assertEquals(k.data['stefan'], 'nope')        