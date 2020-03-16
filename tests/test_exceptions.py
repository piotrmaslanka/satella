import unittest


from satella.exceptions import BaseSatellaError, CustomException, CodedCustomException


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

    def test_coded_exception(self):
        class BaseError(CodedCustomException):
            pass

        class Base2Error(BaseError):
            code = 2

        self.assertIsInstance(BaseError('message', 2), CodedCustomException)
        self.assertIsInstance(Base2Error('message'), CodedCustomException)
        self.assertNotIsInstance(CodedCustomException('message', 2), Base2Error)
        self.assertIsInstance(BaseError('message', 2), Base2Error)
        self.assertIsInstance(Base2Error('message'), Base2Error)

        class DifferentHierarchy(CodedCustomException):
            pass

        self.assertNotIsInstance(DifferentHierarchy('message', 2), Base2Error)
