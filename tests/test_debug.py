import unittest

from satella.debug.environment import enable_environment, Scope


class TestDebug(unittest.TestCase):
    def setUp(self):
        enable_environment()

    def test_scopes(self):
        current_scope = Scope.get_current_scope()
        self.assertIsNotNone(current_scope)

        def test_low_case():
            scope = Scope.get_current_scope()
            scope.test = 5

        test_low_case()
        self.assertEqual(current_scope.test, 5)        # raising data works

