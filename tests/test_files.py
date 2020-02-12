import os
import tempfile
import unittest

from satella.files import read_re_sub_and_write


class TestFiles(unittest.TestCase):
    def setUp(self) -> None:
        self.filename = tempfile.mktemp()

    def tearDown(self) -> None:
        os.unlink(self.filename)

    def test_read_re_sub_and_write(self):
        with open(self.filename, 'w') as f_out:
            f_out.write('RE')

        read_re_sub_and_write(self.filename, r'RE', 'sub')

        with open(self.filename, 'r') as f_in:
            self.assertEqual('sub', f_in.read())

    def test_read_re_sub_and_write_2(self):
        with open(self.filename, 'w') as f_out:
            f_out.write('{2} {3}')

        read_re_sub_and_write(self.filename, r'{(.*?)}', lambda matchobj: matchobj.group(1))

        with open(self.filename, 'r') as f_in:
            self.assertEqual('2 3', f_in.read())
