import unittest


from satella.exceptions import BaseSatellaError, CustomException, CodedCustomException, \
    ImpossibleError, CodedCustomException


class TestExceptions(unittest.TestCase):
    def test_advanced_class_hierarchy(self):
        class A(CodedCustomException):
            code = None  # type: int
            message = ''  # type: str

        class B(A):
            code = 2
            message = 'not readed error'

        b = B()

    def test_coded_custom_exception_no_args(self):
        CodedCustomException()

    def test_impossible_error(self):
        try:
            raise ImpossibleError()
        except Exception:
            self.fail('failed')
        except BaseException:
            pass
        else:
            self.fail('failed')

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
