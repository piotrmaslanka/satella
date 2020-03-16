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
        class Base2Error(CodedCustomException):
            code = 2

        exc = CodedCustomException('message', 2)
        self.assertIsInstance(exc, Base2Error)

        exc = Base2Error()
        del exc.code

        self.assertIsInstance(exc, Base2Error)

