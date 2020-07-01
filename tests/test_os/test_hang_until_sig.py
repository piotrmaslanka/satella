import os
import signal
import sys
import threading
import unittest

from satella import time
from satella.os import hang_until_sig


class TestHangUntilSig(unittest.TestCase):

    @unittest.skipIf('win' in sys.platform, 'Cannot test on Winows')
    def test_hang_until_sig(self):
        def send_sig():
            time.sleep(1)
            os.kill(os.getpid(), signal.SIGINT)

        threading.Thread(target=send_sig).start()
        hang_until_sig()
        self.assertEqual(True, False)
