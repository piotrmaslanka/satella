from satella.instrumentation.logging import LogEntry, LoggerInterface

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
        self.assertEquals('stefan' in k, True)
        self.assertEquals(k.attachments['stefan'], 'nope')
        self.assertEquals(k.data['stefan'], 'nope')

    def test_JSON_serialization(self):
        k = LogEntry('a.b', 'a b').attach('stefan', 'nope').set_data(stefan='nope')

        k = LogEntry.from_JSON(k.to_JSON())

        self.assertEquals('stefan' in k, True)
        self.assertEquals(k.attachments['stefan'], 'nope')
        self.assertEquals(k.data['stefan'], 'nope')        

class LoggerTest(unittest.TestCase):
    """Tests the logging interface"""

    class DummyLoggerIfc(LoggerInterface):
        def __init__(self):
            LoggerInterface.__init__(self)
            self.entries = []

        def produce_entry(self, *args, **kwargs):
            if len(args) == 0:
                return LogEntry('hello', 'test')
            else:
                return LogEntry(args[0], 'test')

        def log_entry(self, entry):
            self.entries.append(entry)

    def test_specialization(self):

        DummyLoggerIfc = self.DummyLoggerIfc

        li = DummyLoggerIfc()
        li.log()
        # test unspecialized
        k = li.entries.pop()
        self.assertEquals(k.who, 'hello')
        self.assertEquals(k.tags, set(('test', )))

        # test single tag specialization
        li_hello = li.specialize(tag='hello')
        li_hello.log()
        k = li.entries.pop()
        self.assertEquals(k.tags, set(('test', 'hello')))

        # test multiple tag specialization
        li_hello2 = li.specialize(tag=('hello', 'goodbye'))
        li_hello2.log()
        k = li.entries.pop()
        self.assertEquals(k.tags, set(('test', 'hello', 'goodbye')))

        # test who specialization
        li_who = li.specialize(who='masters')
        li_who.log()
        k = li.entries.pop()
        self.assertEquals(k.who, 'masters.hello')

        li_who.log('')
        k = li.entries.pop()
        self.assertEquals(k.who, 'masters')
