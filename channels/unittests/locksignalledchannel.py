from threading import Thread
from time import sleep

from satella.channels import LockSignalledChannel, DataNotAvailable, ChannelFailure

import unittest

class LockSignalledChannelTest(unittest.TestCase):

    def test_nonblocking_null_read(self):
        lsc = LockSignalledChannel()
        self.assertRaises(DataNotAvailable, lsc.read, 10)

    def test_nonblocking_foreigndata_read(self):
        lsc = LockSignalledChannel()
        lsc._on_foreign_data('test')
        self.assertEquals(lsc.read(4), 'test')

    def test_nonblocking_localdata_read(self):
        lsc = LockSignalledChannel()
        lsc._on_data('test')
        self.assertEquals(lsc.read(4), 'test')


    def test_blocking_infinite_foreigndata(self):
        class TBI(Thread):
            def __init__(self, lsc):
                Thread.__init__(self)
                self.lsc = lsc

            def run(self):
                sleep(0.1)
                self.lsc._on_foreign_data('test')

        lsc = LockSignalledChannel()
        lsc.blocking = True
        lsc.timeout = None
        TBI(lsc).start()
        self.assertEquals(lsc.read(4), 'test')

    def test_blocking_finite_foreigndata(self):
        class TBI(Thread):
            def __init__(self, lsc):
                Thread.__init__(self)
                self.lsc = lsc

            def run(self):
                sleep(0.1)
                self.lsc._on_foreign_data('test')

        lsc = LockSignalledChannel()
        lsc.blocking = True
        lsc.timeout = 1
        TBI(lsc).start()
        self.assertEquals(lsc.read(4), 'test')

    def test_blocking_finite_null_read(self):
        lsc = LockSignalledChannel()
        lsc.blocking = True
        lsc.timeout = 1
        self.assertRaises(DataNotAvailable, lsc.read, 10)

    def test_blocking_infinite_fail(self):
        class TBI(Thread):
            def __init__(self, lsc):
                Thread.__init__(self)
                self.lsc = lsc

            def run(self):
                sleep(0.1)
                self.lsc._on_foreign_fail()

        lsc = LockSignalledChannel()
        lsc.blocking = True
        lsc.timeout = None
        TBI(lsc).start()
        self.assertRaises(ChannelFailure, lsc.read, 4)

    def test_blocking_finite_fail(self):
        class TBI(Thread):
            def __init__(self, lsc):
                Thread.__init__(self)
                self.lsc = lsc

            def run(self):
                sleep(0.1)
                self.lsc._on_foreign_fail()

        lsc = LockSignalledChannel()
        lsc.blocking = True
        lsc.timeout = 1
        TBI(lsc).start()
        self.assertRaises(ChannelFailure, lsc.read, 4)        