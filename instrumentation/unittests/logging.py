from satella.instrumentation.logging import LogEntry, LogSet

import unittest

class LogsetTest(unittest.TestCase):
    def test_logset_filtering(self):
        f = [
                LogEntry('x.y.z.a', 'satella test'),
                LogEntry('x.y.z', 'satella test'),
                LogEntry('x.y.za', 'satella test'),
                LogEntry('x.y.b', 'satella notest'),
                LogEntry('x.f', 'satella notest'),
            ]

        ls = LogSet(f)

        self.assertEquals(ls.count(), 5)
        self.assertEquals(ls.filter_tag('satella').count(), 5)
        self.assertEquals(ls.filter_tag('test').count(), 3)

        self.assertEquals(ls.filter_hierarchy('x.y.z').count(), 2)
        self.assertEquals(ls.filter_hierarchy('x.y').count(), 4)
        self.assertEquals(ls.filter_hierarchy('x').count(), 5)

        self.assertEquals(ls.filter_hierarchy('x.y').filter_tag('notest').count(), 1)

class LoggingTest(unittest.TestCase):
    def test_base_attachments(self):
        # test whether both variants of .attach() work
        le = LogEntry('satella.instrumentation.unit_tests', ('satella', 'test'))

        le.attach('hello world')
        le.attach('test string', 'hello world')

        self.assertEquals(len(le.attachments), 2)
        self.assertEquals(tuple(le.tags), ('satella', 'test'))

        # test fluid interface of .attach()
        le = LogEntry('satella.instrumentation.unit_tests', 'satella test')

        le = le.attach('hello world').attach('test string', 'hello world')

        self.assertEquals(len(le.attachments), 2)
        self.assertEquals(tuple(le.tags), ('satella', 'test'))
