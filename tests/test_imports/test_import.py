import logging
import unittest
from satella.imports import import_class
import subprocess
import warnings

logger = logging.getLogger(__name__)


class TestImports(unittest.TestCase):
    def test_imports(self):
        import tests.test_imports.importa
        with warnings.catch_warnings(record=True) as warns:
            tests.test_imports.importa.do_import()
        self.assertGreater(len(warns), 0)

        # this as well checks for the namespace's pollution
        self.assertEqual(set(tests.test_imports.importa.importb.__all__),
                         {'logger', 'sub', 'logging', 'add'})

        self.assertEqual(tests.test_imports.importa.importb.add(4, 5), 9)
        self.assertEqual(tests.test_imports.importa.importb.sub(4, 5), -1)
        self.assertRaises(AttributeError, lambda: tests.test_imports.importa.importb.mul(1, 2))

    def test_import_class(self):
        p_open = import_class('subprocess.Popen')
        self.assertIs(p_open, subprocess.Popen)
        self.assertRaises(ImportError, lambda: import_class('subprocess.DoesNotExist'))
