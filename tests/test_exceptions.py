import unittest


from satella.exceptions import BaseSatellaError, CustomException


class TestExceptions(unittest.TestCase):

    def test_exception_kwargs(self):
        e = BaseSatellaError('hello world', label='value')
        self.assertIn("label='value'", repr(e))

    def test_except_inherited(self):
        class InheritedError(CustomException):
            pass

        try:
            raise InheritedError('message', 'arg1', 'arg2')
        except CustomException as e:
            self.assertEqual(str(e), "InheritedError('message', 'arg1', 'arg2')")
        else:
            self.fail()
