import unittest
from satella.coding import metaclass_maker


class MetaA(type):
    pass


class MetaB(type):
    pass


class A(metaclass=MetaA):
    pass


class B(metaclass=MetaB):
    pass


class AB(A, B, metaclass=metaclass_maker):
    pass


class TestMetaclasses(unittest.TestCase):
    def test_metaclasses(self):
        a = AB()

