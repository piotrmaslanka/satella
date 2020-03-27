import os
import tempfile
import unittest
import shutil
from satella.files import read_re_sub_and_write, find_files, split


class TestFiles(unittest.TestCase):
    def test_split(self):
        self.assertEqual(split('c:/windows/system32/system.exe'), ['c:/', 'windows', 'system32',
                                                                   'system32.exe'])
        self.assertEqual(split('~/user/something/./else'), ['~', 'user', 'something', '.',
                                                            'else'])

    def setUp(self) -> None:
        self.filename = tempfile.mktemp()

    def tearDown(self) -> None:
        try:
            os.unlink(self.filename)
        except OSError:
            pass

    def test_find_files(self):
        directory = tempfile.mkdtemp()
        os.mkdir(os.path.join(directory, 'test'))
        with open(os.path.join(directory, 'test', 'test.txt'), 'wb') as f_out:
            f_out.write(b'test')
        self.assertEqual(list(find_files(directory, r'(.*)test(.*)\.txt',
                                         apply_wildcard_to_entire_path=True)), [
            os.path.join(directory, 'test', 'test.txt')])

        self.assertEqual(list(find_files(directory, r'(.*)\.txt')), [
            os.path.join(directory, 'test', 'test.txt')])
        shutil.rmtree(directory)

    def test_read_re_sub_and_write(self):
        with open(self.filename, 'w') as f_out:
            f_out.write('RE')

        read_re_sub_and_write(self.filename, r'RE', 'sub')

        with open(self.filename, 'r') as f_in:
            self.assertEqual('sub', f_in.read())

    def test_read_re_sub_and_write_2(self):
        with open(self.filename, 'w') as f_out:
            f_out.write('{2} {3}')

        read_re_sub_and_write(self.filename, r'{(.*?)}', lambda match_obj: match_obj.group(1))

        with open(self.filename, 'r') as f_in:
            self.assertEqual('2 3', f_in.read())
