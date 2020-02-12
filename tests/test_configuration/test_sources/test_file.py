import os
import tempfile
import unittest

from satella.coding import silence_excs
from satella.configuration.sources import FileSource, FORMAT_SOURCES, \
    DirectorySource
from .utils import SourceTestCase


class TestFileSource(SourceTestCase):
    def setUp(self):
        super(TestFileSource, self).setUp()
        self.filename = tempfile.mktemp()

    @silence_excs(FileNotFoundError)
    def tearDown(self):
        os.unlink(self.filename)

    def check_with_data(self, data: bytes, value: dict):
        with open(self.filename, 'wb') as fout:
            fout.write(data)

        self.assertSourceHas(FileSource(self.filename), value)

    def test_json(self):
        self.check_with_data(b'{"a": 2}', {"a": 2})

    @unittest.skipIf('YAMLSource' not in FORMAT_SOURCES,
                     reason='No pyyaml installed')
    def test_yaml(self):
        self.check_with_data(b"\na: 5\n", {"a": 5})

    @unittest.skipIf('TOMLSource' not in FORMAT_SOURCES,
                     reason='No TOML installed')
    def test_toml(self):
        self.check_with_data(b"a = 5", {"a": 5})


class TestDirectorySource(SourceTestCase):
    def test_directory_invalids(self):
        with tempfile.TemporaryDirectory() as outdir:
            self.filename = outdir
            self.makefile("valid-json.json", b'''{
  "amqp": "amqp",
  "logstash": {
    "host": "localhost",
    "port": 9600
  }
}
''')
            self.makefile("invalid-json.json", b'''{"CI": true''')
            self.ds = DirectorySource(outdir, on_fail=DirectorySource.SILENT)
            self.assertEqual(self.ds.provide(),
                             {'amqp': 'amqp', 'logstash': {'host': 'localhost', 'port': 9600}})

    def test_directory_source(self):
        with tempfile.TemporaryDirectory() as outdir:
            self.filename = outdir
            self.assertTrue(os.path.isdir(outdir))
            self.ds = DirectorySource(outdir, scan_subdirectories=True)
            self.makefile('config.json', b'{"a": [2]}')
            self.makefile('config2.json', b'{"a": [2]}')
            os.mkdir(os.path.join(outdir, 'temp1'))
            self.makefile(os.path.join(outdir, 'temp1', 'config3.json'),
                          b'{"a": [23]}')
            self.assertSourceHas(self.ds, set((2, 2, 23)), postop=lambda x: set(x['a']))

    def makefile(self, name: str, value: bytes):
        with open(os.path.join(self.filename, name), 'wb') as fout:
            fout.write(value)
