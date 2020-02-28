import unittest
import typing as tp
from satella.coding import attach_arguments


class TestDecorators(unittest.TestCase):
    def test_attach_arguments(self):
        @attach_arguments(label=2)
        def test_me(**kwargs):
            self.assertEqual(kwargs, {'label': 2, 'value': 4})

        test_me(value=4)
