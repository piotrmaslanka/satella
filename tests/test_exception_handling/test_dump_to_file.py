import io
import os
import pickle
import tempfile

from satella.coding import silence_excs
from satella.exception_handling import DumpToFileHandler
from satella.instrumentation import Traceback
from . import ExceptionHandlingTestCase


class TestDumpToFile(ExceptionHandlingTestCase):
    def test_dump_to_file(self):
        sq, sa, tf = io.StringIO(), io.StringIO(), tempfile.mktemp()
        op = io.BytesIO()

        self.exception_handler = DumpToFileHandler(human_readables=[sq, sa, tf],
                                                   trace_pickles=[op])
        self.exception_handler.install()

        try:
            def makeexc():
                print(hello)

            self.make_exception(makeexc)

            sq, sa = sq.getvalue(), sa.getvalue()
            with open(tf, 'r', encoding='utf8') as fi:
                sb = fi.read()

            def assertIn(txt):
                self.assertIn(txt, sq)
                self.assertIn(txt, sa)
                self.assertIn(txt, sb)

            assertIn('NameError')
            assertIn('hello')
        finally:
            with silence_excs(FileNotFoundError):
                os.unlink(tf)

        tbp = pickle.loads(op.getvalue())
        self.assertIsInstance(tbp, Traceback)
