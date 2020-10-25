import logging
import queue
import unittest
from socket import socket

from satella.coding import wraps, chain_functions, postcondition, \
    log_exceptions, queue_get, precondition, short_none
from satella.coding.decorators import auto_adapt_to_methods, attach_arguments, \
    execute_before, loop_while, memoize, copy_arguments
from satella.coding.predicates import x
from satella.exceptions import PreconditionError

logger = logging.getLogger(__name__)


class TestDecorators(unittest.TestCase):

    def test_copy_arguments(self):
        @copy_arguments()
        def alter_dict(dct):
            return dct.pop('a')

        b = {'a': 5}
        self.assertEqual(alter_dict(b), 5)
        self.assertEqual(b, {'a': 5})

    def test_memoize(self):
        a = {'call_count': 0}

        @memoize
        def memoizer(b):
            a['call_count'] += 1
            return b

        five = memoizer(5)
        self.assertEqual(a['call_count'], 1)
        five = memoizer(5)
        self.assertEqual(a['call_count'], 1)
        five = memoizer(6)
        self.assertEqual(a['call_count'], 2)

    def test_loop_while(self):
        class MyLooped:
            terminating = False
            i = 0

            @loop_while(x.i < 10)
            def run(self):
                self.i += 1

        a = MyLooped()
        a.run()
        self.assertGreaterEqual(a.i, 10)
        b = {'i': 0}

        @loop_while(lambda: b['i'] < 10)
        def run():
            nonlocal b
            b['i'] += 1

        run()
        self.assertGreaterEqual(b['i'], 10)

    def test_execute_before(self):
        a = 0

        @execute_before
        def increase_a(factor=1):
            nonlocal a
            a += factor

        @increase_a(factor=2)
        def launch_me():
            nonlocal a
            a += 1

        launch_me()
        self.assertEqual(a, 3)

    def test_precondition_none(self):
        @precondition(short_none('x == 2'))
        def x(y):
            return y
        x(2)
        x(None)
        self.assertRaises(PreconditionError, lambda: x(3))

    def test_queue_get(self):
        class Queue:
            def __init__(self):
                self.queue = queue.Queue()
                self.on_empty_called = False

            @queue_get('queue', timeout=0, method_to_execute_on_empty='process_on_empty')
            def process(self, item):
                pass

            def process_on_empty(self):
                self.on_empty_called = True

        q = Queue()
        q.queue.put(True)
        q.process()
        q.process()
        self.assertTrue(q.on_empty_called)

    def test_log_exceptions(self):
        try:
            with log_exceptions(logger):
                int('a')
        except ValueError:
            pass
        else:
            self.fail('exception swallowed!')

    def test_postcondition(self):
        @postcondition(lambda x: x == 2)
        def return_a_value(x):
            return x

        self.assertEqual(return_a_value(2), 2)
        self.assertRaises(PreconditionError, lambda: return_a_value(3))

    def test_auto_adapt_to_methods(self):
        @auto_adapt_to_methods
        def times_two(fun):
            def outer(a):
                return fun(a * 2)

            return outer

        class Test:
            @times_two
            def twice(self, a):
                return a * 2

        @times_two
        def twice(a):
            return a * 2

        self.assertEqual(Test().twice(2), 8)
        self.assertEqual(twice(2), 8)

    def test_chain_kwargs(self):
        @chain_functions
        def double_arguments(**kwargs):
            kwargs['a'] = kwargs['a'] * 2
            return kwargs

        @double_arguments
        def multiply_times_two(**kwargs):
            return kwargs['a'] * 2

        self.assertEqual(multiply_times_two(a=2), 8)

    def test_chain(self):
        @chain_functions
        def double_arguments(a):
            return a * 2

        @double_arguments
        def multiply_times_two(a):
            return a * 2

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
