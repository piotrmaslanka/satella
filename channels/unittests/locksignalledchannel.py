from threading import Thread
from time import sleep

from satella.channels import LockSignalledChannel, DataNotAvailable, \
                             ChannelFailure, ChannelClosed

import unittest

class LockSignalledChannelTest(unittest.TestCase):
    """Tests for lock-signalled channels without the use of a handling layer"""

    def test_nonblocking_null_read(self):
        lsc = LockSignalledChannel()
        self.assertRaises(DataNotAvailable, lsc.read, 10)

    def test_nonblocking_foreigndata_read(self):
        lsc = LockSignalledChannel()
        lsc._on_async_data('test')
        self.assertEquals(lsc.read(4), 'test')

    def test_nonblocking_localdata_lessread(self):
        lsc = LockSignalledChannel()
        lsc._on_data('test')
        self.assertEquals(lsc.read(100, less=True), 'test')

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
                self.lsc._on_async_data('test')

        lsc = LockSignalledChannel()
        lsc.blocking = True
        lsc.timeout = None
        TBI(lsc).start()
        self.assertEquals(lsc.read(4), 'test')

    def test_blocking_infinite_foreigndata_lessread(self):
        class TBI(Thread):
            def __init__(self, lsc):
                Thread.__init__(self)
                self.lsc = lsc

            def run(self):
                sleep(0.5)
                self.lsc._on_async_data('test')

        lsc = LockSignalledChannel()
        lsc.blocking = True
        lsc.timeout = None
        TBI(lsc).start()
        self.assertEquals(lsc.read(100, less=True), 'test')

    def test_blocking_finite_foreigndata(self):
        class TBI(Thread):
            def __init__(self, lsc):
                Thread.__init__(self)
                self.lsc = lsc

            def run(self):
                sleep(0.1)
                self.lsc._on_async_data('test')

        lsc = LockSignalledChannel()
        lsc.blocking = True
        lsc.timeout = 1
        TBI(lsc).start()
        self.assertEquals(lsc.read(4), 'test')

    def test_blocking_finite_foreigndata_lessread(self):
        class TBI(Thread):
            def __init__(self, lsc):
                Thread.__init__(self)
                self.lsc = lsc

            def run(self):
                sleep(0.5)
                self.lsc._on_async_data('test')

        lsc = LockSignalledChannel()
        lsc.blocking = True
        lsc.timeout = 1
        TBI(lsc).start()
        self.assertEquals(lsc.read(100, less=True), 'test')        

    def test_nonblocking_finite_null_read(self):
        lsc = LockSignalledChannel()
        lsc.blocking = False
        lsc.timeout = 0
        self.assertRaises(DataNotAvailable, lsc.read, 10)

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
                self.lsc._on_async_fail()

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
                self.lsc._on_async_fail()

        lsc = LockSignalledChannel()
        lsc.blocking = True
        lsc.timeout = 1
        TBI(lsc).start()
        self.assertRaises(ChannelFailure, lsc.read, 4)        


    def test_blocking_infinite_close(self):
        class TBI(Thread):
            def __init__(self, lsc):
                Thread.__init__(self)
                self.lsc = lsc

            def run(self):
                sleep(0.1)
                self.lsc._on_async_close()

        lsc = LockSignalledChannel()
        lsc.blocking = True
        lsc.timeout = None
        TBI(lsc).start()
        self.assertRaises(ChannelClosed, lsc.read, 4)

    def test_blocking_finite_close(self):
        class TBI(Thread):
            def __init__(self, lsc):
                Thread.__init__(self)
                self.lsc = lsc

            def run(self):
                sleep(0.1)
                self.lsc._on_async_close()

        lsc = LockSignalledChannel()
        lsc.blocking = True
        lsc.timeout = 1
        TBI(lsc).start()
        self.assertRaises(ChannelClosed, lsc.read, 4)                