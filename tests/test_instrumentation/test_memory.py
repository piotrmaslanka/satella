import logging
import os
import platform
import signal
import sys

from satella.instrumentation import install_dump_frames_on
from satella.instrumentation.memory import MemoryPressureManager, CustomCondition, All, Any, \
    dump_memory_on, get_size
import time
import unittest
logger = logging.getLogger(__name__)


class OnDemandCondition(CustomCondition):
    def __init__(self):
        self.value = False
        super().__init__(lambda: self.value)

    def can_fire(self, *args) -> bool:
        return self.value


class TestMemory(unittest.TestCase):
    def test_get_size_dict(self):
        a = {'aba': 'aba'}

        class Aba:
            def __init__(self):
                self.aba = 'aba'

        if platform.python_implementation() == 'PyPy':
            self.assertRaises(RuntimeError, get_size, a)
            self.assertRaises(RuntimeError, get_size, Aba())
        else:
            self.assertGreater(get_size(a), 6)
            self.assertGreater(get_size(Aba()), 6)

    @unittest.skipIf(sys.platform == 'win32', 'testable only on unices')
    def test_install_dump_on(self):
        install_dump_frames_on(signal.SIGUSR1)
        os.kill(os.getpid(), signal.SIGUSR1)

    @unittest.skipIf(platform.python_implementation() == 'PyPy', 'does not work on PyPy')
    def test_get_size(self):
        a = 'a' * 1024
        self.assertGreaterEqual(get_size(a), 1024)

    @unittest.skipIf(platform.python_implementation() != 'PyPy', 'requires PyPy')
    def test_get_size_runtime_error(self):
        a = 'a' * 1024
        self.assertRaises(RuntimeError, lambda: get_size(a))

    def test_dump_memory(self):
        dump_memory_on()

    def test_memory(self):
        odc = OnDemandCondition()

        a = {'memory': False,
             'calls': 0,
             'improved': False,
             'times_entered_1': 0,
             'level_2_engaged': False,
             'level_2_confirmed': False,
             'cancelled': 0,
             'mem_normal': 0}

        class ObjectToCleanup:
            def __init__(self):
                self.cleaned_up = False

            def cleanup(self):
                self.cleaned_up = True

        obj1 = ObjectToCleanup()
        obj2 = ObjectToCleanup()

        cc = CustomCondition(lambda: a['level_2_engaged'])

        MemoryPressureManager(None, [odc, All(cc, Any(cc, cc))], 2)
        MemoryPressureManager.cleanup_on_entered(1, obj1)
        MemoryPressureManager.cleanup_on_entered(2, obj2)

        def memory_normal():
            nonlocal a
            a['mem_normal'] += 1

        def cancel():
            nonlocal a
            a['cancelled'] += 1
        MemoryPressureManager.register_on_memory_normal(memory_normal)

        cc = MemoryPressureManager.register_on_entered_severity(1)(cancel)

        @MemoryPressureManager.register_on_entered_severity(2)
        def call_on_level_2():
            a['level_2_confirmed'] = True

        @MemoryPressureManager.register_on_remaining_in_severity(1)
        def call_on_memory_still():
            a['calls'] += 1

        @MemoryPressureManager.register_on_entered_severity(1)
        def call_on_no_memory():
            a['memory'] = True
            a['times_entered_1'] += 1

        @MemoryPressureManager.register_on_left_severity(1)
        def call_improved():
            a['improved'] = True

        self.assertFalse(a['memory'])
        self.assertFalse(a['improved'])
        self.assertEqual(a['mem_normal'], 0)
        time.sleep(3)
        odc.value = True
        time.sleep(5)
        self.assertEqual(a['cancelled'], 1)
        cc.cancel()
        self.assertTrue(a['memory'])
        self.assertFalse(a['improved'])
        self.assertGreater(a['calls'], 0)
        self.assertTrue(obj1.cleaned_up)
        self.assertEqual(a['times_entered_1'], 1)
        del obj1
        odc.value = False
        time.sleep(3)
        self.assertTrue(a['improved'])
        self.assertEqual(a['times_entered_1'], 1)
        self.assertTrue(a['memory'])
        self.assertEqual(a['mem_normal'], 1)
        a['level_2_engaged'] = True
        time.sleep(3)
        self.assertLessEqual(len(MemoryPressureManager().objects_to_cleanup_on_entered[1]), 1)
        self.assertEqual(MemoryPressureManager().severity_level, 2)
        self.assertEqual(a['cancelled'], 1)
        self.assertEqual(a['times_entered_1'], 2)
        self.assertTrue(a['level_2_confirmed'])
        self.assertEqual(a['mem_normal'], 1)
        self.assertTrue(obj2.cleaned_up)
