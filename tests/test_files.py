import io
import os
from os.path import join
import tempfile
import unittest
import shutil
from satella.files import read_re_sub_and_write, find_files, split, read_in_file, write_to_file, \
    write_out_file_if_different, make_noncolliding_name, try_unlink, DevNullFilelikeObject, \
    read_lines, AutoflushFile


def putfile(path: str) -> None:
    with open(path, 'wb') as f_out:
        f_out.write(b'\x32')


class TestFiles(unittest.TestCase):

    def test_read_nonexistent_file(self):
        self.assertRaises(FileNotFoundError, lambda: read_in_file('moot'))

    def test_autoflush_file(self):
        af = AutoflushFile('test3.txt', 'w+', encoding='utf-8')
        try:
            af.write('test')
            assert read_in_file('test3.txt', encoding='utf-8') == 'test'
            af.write('test2')
            assert read_in_file('test3.txt', encoding='utf-8') == 'testtest2'
            af.truncate(4)
            assert read_in_file('test3.txt', encoding='utf-8') == 'test'
        finally:
            af.close()
            try_unlink('test3.txt')

    def test_read_lines(self):
        lines = read_lines('LICENSE')
        self.assertTrue(all(lines))

        with open('test.tmp', 'w') as f_out:
            f_out.write('''line1
            line2
            line3
            
            ''')

        self.assertEqual(read_lines('test.tmp'), ['line1', 'line2', 'line3'])

    def test_devnullfilelikeobject(self):
        null = DevNullFilelikeObject()
        self.assertEqual(null.write('ala'), 3)
        assert null.seek(0) == 0
        assert null.tell() == 0
        assert null.seekable()
        assert null.truncate(0) == 0
        self.assertEqual(null.write(b'ala'), 3)
        self.assertEqual(null.read(), '')
        self.assertEqual(null.read(7), '')
        null.flush()
        null.close()
        self.assertRaises(ValueError, lambda: null.write('test'))
        self.assertRaises(ValueError, lambda: null.flush())
        self.assertRaises(ValueError, lambda: null.read())
        null.close()

    def try_directory(self):
        os.system('mkdir test')
        self.assertRaises(FileNotFoundError, lambda: read_in_file('test'))
        self.assertEqual(b'test', read_in_file('test', default=b'test'))
        os.system('rm -rf test')
        self.assertRaises(FileNotFoundError, lambda: read_in_file('test'))
        self.assertEqual(b'test', read_in_file('test', default=b'test'))

    def test_make_noncolliding_name(self):
        with open('test.txt', 'w') as f_out:
            f_out.write('test')
        self.assertEqual(make_noncolliding_name('test.txt'), 'test.1.txt')
        self.assertTrue(try_unlink('test.txt'))
        self.assertFalse(try_unlink('test.txt'))

    def test_write_out_file_if_different(self):
        try:
            self.assertTrue(write_out_file_if_different('test', 'test', 'UTF-8'))
            self.assertFalse(write_out_file_if_different('test', 'test', 'UTF-8'))
        finally:
            os.unlink('test')

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
