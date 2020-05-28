import os
from os.path import join
import tempfile
import unittest
import shutil
from satella.files import read_re_sub_and_write, find_files, split, read_in_file, write_to_file


def putfile(path: str) -> None:
    with open(path, 'wb') as f_out:
        f_out.write(b'\x32')


class TestFiles(unittest.TestCase):

    def test_read_in_and_write_to(self):
        data = 'żażółć gęślą jaźń'
        write_to_file('temp.tmp', data, 'UTF-8')
        data2 = read_in_file('temp.tmp', 'UTF-8')
        self.assertEqual(data, data2)

    def test_split(self):
        self.assertIn(split('c:/windows/system32/system32.exe'), [['c:', 'windows', 'system32',
                                                                     'system32.exe'],
                                                                  ['c:/', 'windows', 'system32',
                                                                   'system32.exe']
                                                                  ])
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
        os.mkdir(join(directory, 'test'))
        putfile(join(directory, 'test', 'test.txt'))
        os.mkdir(join(directory, 'test', 'test'))
        putfile(join(directory, 'test', 'test', 'test.txt'))
        putfile(join(directory, 'test', 'test', 'test2.txt'))
        self.assertEqual(set(find_files(directory, r'(.*)test(.*)\.txt',
                                         apply_wildcard_to_entire_path=True)), {
            join(directory, 'test', 'test.txt'),
            join(directory, 'test', 'test', 'test.txt'),
            join(directory, 'test', 'test', 'test2.txt')
        })

        self.assertEqual(set(find_files(directory, r'(.*)\.txt')), {
            join(directory, 'test', 'test.txt'),
            join(directory, 'test', 'test', 'test.txt'),
            join(directory, 'test', 'test', 'test2.txt')
        })
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
