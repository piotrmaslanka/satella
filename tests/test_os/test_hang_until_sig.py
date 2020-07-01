import os
import signal
import sys
import threading
import unittest
import time
import multiprocessing

from satella.os import hang_until_sig


class TestHangUntilSig(unittest.TestCase):

    def test_hang_until_sig(self):

        def child_process():
            hang_until_sig()

        mp = multiprocessing.Process(target=child_process)
        mp.start()

        time.sleep(1)
        os.kill(mp.pid, signal.SIGTERM)
        time.sleep(2)
        os.wait()
