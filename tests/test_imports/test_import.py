import logging
import unittest

logger = logging.getLogger(__name__)


class TestImports(unittest.TestCase):
    def test_imports(self):
        import tests.test_imports.importa
        tests.test_imports.importa.do_import()

        # this as well checks for the namespace's pollution
        self.assertEqual(set(tests.test_imports.importa.importb.__all__),
                         {'logger', 'sub', 'logging', 'add'})

        self.assertEqual(tests.test_imports.importa.importb.add(4, 5), 9)
        self.assertEqual(tests.test_imports.importa.importb.sub(4, 5), -1)
        self.assertRaises(AttributeError, lambda: tests.test_imports.importa.importb.mul(1, 2))
