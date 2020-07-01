import unittest
import sys
from satella.processes import call_and_return_stdout


class TestProcesses(unittest.TestCase):
    @unittest.skipIf('win' in sys.platform, 'Running on Windows')
    def test_timeouts(self):
        self.assertRaises(TimeoutError, lambda: call_and_return_stdout('sleep 5',
                                                                       shell=True, timeout=3))

    @unittest.skipIf('win' in sys.platform, 'Running on Windows')
    def test_return_stdout(self):
        output = call_and_return_stdout('ls .', shell=True, timeout=3, expected_return_code=0)
        self.assertIn(b'requirements.txt', output)

    @unittest.skipIf('win' in sys.platform or sys.version_info.minor < 6, 'Running on Windows or Python 3.5')
    def test_return_encoding(self):
        output = call_and_return_stdout('ls .', shell=True, encoding='utf8', timeout=3)
        self.assertIn('requirements.txt', output)
