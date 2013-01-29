from satella.threads import BaseThread
from time import sleep

import unittest

class ThreadingTest(unittest.TestCase):

    def test_terminate(self):
        """Tests whether setting termination flag works
        and start() returns the thread"""

        class TTT(BaseThread):
            def run(self):
                while not self._terminating:
                    sleep(0.1)

        k = TTT().start()
        self.assertEquals(type(k), TTT)
        sleep(0.2)
        k.terminate()
        k.join()

        self.assertEquals(k._terminating, True)