from satella.instrumentation.logging import LogEntry, LoggerInterface
# LoggerInterface is implemented only as API check

import unittest

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