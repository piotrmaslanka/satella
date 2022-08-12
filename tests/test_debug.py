import unittest

from satella.debug.environment import enable_environment, Scope


class TestDebug(unittest.TestCase):
    def test_scopes(self):
        enable_environment()
        from satella.debug.environment import tracing
        self.assertTrue(tracing.ENVIRONMENT_ENABLED)
        current_scope = Scope.get_current_scope()
        self.assertIsNotNone(current_scope)

        def test_low_case():
            scope = Scope.get_current_scope()
            scope.test = 5

        test_low_case()
        self.assertEqual(current_scope.test, 5)        # raising data works

