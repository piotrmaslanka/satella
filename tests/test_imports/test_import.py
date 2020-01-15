import logging
import unittest

logger = logging.getLogger(__name__)


class TestImports(unittest.TestCase):
    def test_imports(self):
        import tests.test_imports.importa
        tests.test_imports.importa.do_import()

        tests.test_imports.importa.importb.__all__

        self.assertEqual(tests.test_imports.importa.importb.add(4, 5), 9)
        self.assertEqual(tests.test_imports.importa.importb.sub(4, 5), -1)
