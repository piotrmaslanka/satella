import io
import os
import pickle
import tempfile

from satella.coding import silence_excs
from satella.exception_handling import DumpToFileHandler
from satella.instrumentation import Traceback
from . import ExceptionHandlingTestCase


class TestDumpToFile(ExceptionHandlingTestCase):
    def setUp(self):
        self.sq, self.sa, self.tf = io.StringIO(), io.StringIO(), tempfile.mktemp()
        self.op = io.BytesIO()
        self.exception_handler = DumpToFileHandler(human_readables=[self.sq, self.sa, self.tf, None],
                                                   trace_pickles=[self.op])
        self.exception_handler.install()

    def tearDown(self):
        self.exception_handler.uninstall()

    def test_dump_to_file(self):
        try:
            def makeexc():
                print(hello)  # raises NameError

            self.make_exception(makeexc)

            self.sq, self.sa = self.sq.getvalue(), self.sa.getvalue()
            with open(self.tf, 'r', encoding='utf8') as fi:
                sb = fi.read()

            def assertIn(txt):
                self.assertIn(txt, self.sq)
                self.assertIn(txt, self.sa)
                self.assertIn(txt, sb)

            assertIn('NameError')
            assertIn('hello')
        finally:
            with silence_excs(FileNotFoundError):
                os.unlink(self.tf)

        tbp = pickle.loads(self.op.getvalue())
        self.assertIsInstance(tbp, Traceback)
