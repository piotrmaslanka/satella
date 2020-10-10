import queue
import unittest

from satella.coding.structures import Singleton, SingletonWithRegardsTo, \
    get_instances_for_singleton, delete_singleton_for
from satella.coding import queue_iterator


class TestSingleton(unittest.TestCase):

    def test_queue_iterator(self):
        q = queue.Queue()
        q.put(2)
        q.put(5)
        self.assertEqual(list(queue_iterator(q)), [2, 5])

    def test_singleton(self):
        @Singleton
        class MyClass(object):
            def __init__(self):
                self.a = 5

        a = MyClass()
        b = MyClass()

        a.a = 6

        self.assertEqual(b.a, 6)

    def test_singleton_taking_arguments(self):
        @Singleton
        class MyClass(object):
            def __init__(self, a):
                self.a = a

        a = MyClass(5)
        b = MyClass(6)

        self.assertEqual(a.a, 5)
        self.assertEqual(b.a, 5)

    def test_singleton_with_regards_to(self):
        @SingletonWithRegardsTo(num_args=1)
        class MyClass:
            def __init__(self, device_id: str):
                self.device_id = device_id

        a = MyClass('a')
        b = MyClass('b')
        c = MyClass('a')
        self.assertIs(a, c)
        self.assertIsNot(a, b)
        self.assertEqual(a.device_id, 'a')
        self.assertEqual(b.device_id, 'b')
        a.device_id = 'c'
        self.assertEqual(c.device_id, 'c')
        self.assertEqual(set(get_instances_for_singleton(MyClass)), {('a',), ('b',)})
        delete_singleton_for(MyClass, 'a')
        self.assertEqual(set(get_instances_for_singleton(MyClass)), {('b',)})
