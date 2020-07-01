import os
import signal
import unittest
import time
import multiprocessing

from satella.os import hang_until_sig


class TestHangUntilSig(unittest.TestCase):

    def test_hang_until_sig(self):

        def child_process():
            time.sleep(1)
            os.kill(os.getppid(), signal.SIGTERM)

        mp = multiprocessing.Process(target=child_process)
        mp.start()

        hang_until_sig()
        os.wait()
