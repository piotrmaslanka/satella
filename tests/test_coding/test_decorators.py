import unittest
from socket import socket
from satella.coding import attach_arguments, wraps, chain


class TestDecorators(unittest.TestCase):

    def test_chain_kwargs(self):
        @chain
        def double_arguments(**kwargs):
            kwargs['a'] = kwargs['a']*2
            return kwargs

        @double_arguments
        def multiply_times_two(**kwargs):
            return kwargs['a']*2

        self.assertEqual(multiply_times_two(a=2), 8)

    def test_chain(self):
        @chain
        def double_arguments(a):
            return a*2

        @double_arguments
        def multiply_times_two(a):
            return a*2

        self.assertEqual(multiply_times_two(2), 8)

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

    def test_wraps_onfunction(self):
        def my_fun(a):
            """Returns the argument"""
            return a

        @wraps(my_fun)
        def f(a):
            return my_fun(a)

        self.assertEqual(f.__doc__, my_fun.__doc__)
        self.assertEqual(f.__name__, my_fun.__name__)
        self.assertEqual(f.__module__, my_fun.__module__)
