import unittest
from socket import socket
from satella.coding import attach_arguments, wraps


class TestDecorators(unittest.TestCase):
    def test_attach_arguments(self):
        @attach_arguments(label=2)
        def test_me(**kwargs):
            self.assertEqual(kwargs, {'label': 2, 'value': 4})

        test_me(value=4)

    def test_wraps(self):
        @wraps(socket)
        class MySocket(socket):
            pass

        self.assertEqual(MySocket.__name__, socket.__name__)
        self.assertEqual(MySocket.__doc__, socket.__doc__)
        self.assertEqual(MySocket.__module__, socket.__module__)
