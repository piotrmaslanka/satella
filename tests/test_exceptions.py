import unittest
import typing as tp
from satella.exceptions import BaseSatellaException


class TestExceptions(unittest.TestCase):
    def test_exception(self):
        try:
            raise BaseSatellaException('message', 'arg1', 'arg2')
        except BaseSatellaException as e:
            self.assertIn('arg1', str(e))
            self.assertIn('arg2', str(e))
            self.assertIn('BaseSatellaException', str(e))
        else:
            self.fail()

    def test_except_inherited(self):
        class InheritedException(BaseSatellaException):
            pass

        try:
            raise InheritedException('message', 'arg1', 'arg2')
        except BaseSatellaException as e:
            self.assertIn('arg1', str(e))
            self.assertIn('arg2', str(e))
            self.assertIn('InheritedException', str(e))
        else:
            self.fail()
