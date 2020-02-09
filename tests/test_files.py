import unittest
import os
import tempfile
from satella.files import read_re_sub_and_write


class TestFiles(unittest.TestCase):
    def test_read_re_sub_and_write(self):
        filename = tempfile.mktemp()
        with open(filename, 'w') as f_out:
            f_out.write('RE')

        read_re_sub_and_write(filename, r'RE', 'sub')

        with open(filename, 'r') as f_in:
            self.assertEqual('sub', f_in.read())

        os.unlink(filename)
