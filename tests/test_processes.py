import unittest
import sys
from satella.processes import call_and_return_stdout


class TestProcesses(unittest.TestCase):
    @unittest.skipIf('win' in sys.platform, 'Running on Windows')
    def test_return_stdout(self):
        output = call_and_return_stdout('cat /proc/meminfo', shell=True, timeout=3)
        self.assertIn(b'MemTotal', output)

    @unittest.skipIf('win' in sys.platform or sys.version_info.minor < 6, 'Running on Windows or Python 3.5')
    def test_return_encoding(self):
        output = call_and_return_stdout('cat /proc/meminfo', shell=True, encoding='utf8', timeout=3)
        self.assertIn('MemTotal', output)
