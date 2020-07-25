import os
import sys
import unittest

from satella.os.misc import suicide


class TestSuicide(unittest.TestCase):
    @unittest.skipIf('win' in sys.platform, 'Running on Windows')
    def test_suicide(self):
        pcid = os.fork()

        if pcid == 0:
            suicide()

        self.assertEqual(os.wait(), (pcid, 9))
