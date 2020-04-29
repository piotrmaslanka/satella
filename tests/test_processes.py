import unittest
import sys
from satella.processes import call_and_return_stdout


class TestProcesses(unittest.TestCase):
    @unittest.skipIf('win' in sys.platform, 'Running on Windows')
    def test_return_stdout(self):
        output = call_and_return_stdout('cat /proc/meminfo', shell=True, encoding='utf8')
        self.assertIn('MemTotal', output)

        output = call_and_return_stdout('cat /proc/meminfo', shell=True)
        self.assertIn(b'MemTotal', output)
