# coding=UTF-8
from __future__ import print_function, absolute_import, division

import platform
import time
import unittest

from satella.coding.concurrent import TerminableThread, CallableGroup


class TestCallableGroup(unittest.TestCase):

    def test_terminable_thread(self):
        class MyTerminableThread(TerminableThread):
            def loop(self):
                time.sleep(0.5)

        mtt = MyTerminableThread()
        mtt.start()
        mtt.terminate().join()

    @unittest.skipIf(platform.python_implementation() == 'PyPy', 'force=True doesn''t work on PyPy')
    def test_terminable_thread_force(self):
        class MyTerminableThread(TerminableThread):
            def run(self):
                a = 0
                while True:
                    time.sleep(0.5)
                    a += 1

        mtt = MyTerminableThread(daemon=True)
        mtt.start()
        mtt.terminate(force=True)
        mtt.join(3)
        self.assertFalse(mtt.is_alive())

    def test_callable_group_some_raise(self):
        cg = CallableGroup(gather=True)
        cg.add(lambda: dupa)
        cg.add(lambda: 5)
        self.assertRaises(NameError, lambda: cg())

        cg = CallableGroup(gather=True, swallow_exceptions=True)
        cg.add(lambda: dupa)
        cg.add(lambda: 5)
        self.assertEquals(cg()[1], 5)
        self.assertIsInstance(cg()[0], NameError)

    def test_callable_group(self):
        a = {
            'a': False,
            'b': False
        }

        opF = lambda what: lambda: a.__setitem__(what, True)

        cg = CallableGroup()

        cg.add(opF('a'))
        cg.add(opF('b'))

        cg()

        self.assertTrue(all(a.values()))
