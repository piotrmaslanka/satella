import unittest
from satella.coding import metaclass_maker


class TestMetaclasses(unittest.TestCase):
    def test_metaclasses(self):
        class MetaA(type):
            pass

        class MetaB(type):
            pass

        class A:
            __metaclass__ = MetaA

        class B:
            __metaclass__ = MetaB

        class AB(A, B):
            __metaclass__ = metaclass_maker()

        a = AB()

