import unittest
from concurrent.futures.thread import ThreadPoolExecutor

from satella.coding.call_hierarchy import Call, CallWithArgumentSet, Reduce, CallIf, \
    ExecutionEnvironment, package_for_execution, call, current_args, current_kwargs, current_history


class TestCallHierarchy(unittest.TestCase):
    def test_call(self):
        call_ = Call(lambda: 5)
        self.assertEqual(call_(), 5)

    def test_exec_parallel(self):
        arg_sets = []

        def mult(y):
            return y*2

        for value in [1, 2, 3, 4, 5, 6, 7]:
            arg_sets.append(((value, ), {}))

        calls = []
        for i, _ in enumerate(arg_sets):
            calls.append(CallWithArgumentSet(mult, i))
        call_v = Reduce(*calls, reducing_op=lambda a, b: a+b, starting_value=0)
        tpe = ThreadPoolExecutor(max_workers=4)

        ee = ExecutionEnvironment(arg_sets, tpe)
        pp = package_for_execution(call_v, ee)
        self.assertEqual(pp(), 56)

    def test_current(self):
        @call
        def nested(a: int):
            self.assertEqual(len(current_history()), 2)

        @call
        def call_me(a: int):
            self.assertEqual(a, 5)
            self.assertEqual(current_args(), (5, ))
            self.assertEqual(current_kwargs(), {})
            nested()

        call_me(5)

    def test_arg_sets(self):
        def add(a, b):
            return a+b

        call1 = CallWithArgumentSet(add, 0)
        call2 = CallWithArgumentSet(add, 1)
        call_v = Reduce(call1, call2, reducing_op=lambda a, b: a+b, starting_value=0)
        ee = ExecutionEnvironment([((1, 2), {}), ((3, 4), {})])
        self.assertEqual(ee(call_v), 10)

    def test_call_if(self):
        a = {'test': True, 'b': 0}

        def a_is_true():
            nonlocal a
            return a['test']

        def incr_b():
            nonlocal a
            a['b'] += 1

        call_if_true = CallIf(a_is_true, incr_b)

        call_if_true()
        self.assertEqual(a['b'], 1)
        a['test'] = False
        call_if_true()
        self.assertEqual(a['b'], 1)
