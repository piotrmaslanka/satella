import os
import signal
import sys
import unittest
import time
import multiprocessing

from satella.os import hang_until_sig


class TestHangUntilSig(unittest.TestCase):

    @unittest.skipIf('win' in sys.platform, 'Needs a POSIX to run')
    def test_hang_until_sig(self):

        def child_process():
            time.sleep(1)
            os.kill(os.getppid(), signal.SIGTERM)

        mp = multiprocessing.Process(target=child_process)
        mp.start()
        try:
            hang_until_sig()
        finally:
            os.wait()
