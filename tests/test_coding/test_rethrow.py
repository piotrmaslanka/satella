import logging
import unittest

from satella.coding import rethrow_as, silence_excs, catch_exception, log_exceptions, raises_exception

logger = logging.getLogger(__name__)


class TestStuff(unittest.TestCase):

    def test_raises(self):
        self.assertTrue(raises_exception(NameError, lambda: name_error))
        self.assertFalse(raises_exception(NameError, lambda: None))

    def test_log_exceptions_decorator(self):

        @log_exceptions(logger, logging.CRITICAL)
        def get_me():
            yield 2
            yield 4
            raise KeyError()

        try:
            with log_exceptions(logger, exc_types=KeyError):
                for i in get_me():
                    pass
        except KeyError:
            pass
        else:
            self.fail('KeyError not raised')

    def test_log_exceptions(self):
        a = 5

        @silence_excs(KeyError)
        @log_exceptions(logger, logging.CRITICAL, '{a} {e} {args}', locals())
        def raise_keyerror():
            raise KeyError('hello')

        raise_keyerror()

        with silence_excs(KeyError):
            with log_exceptions(logger):
                raise_keyerror()

    def test_returns(self):
        @silence_excs(ValueError, returns=5)
        def throw_value_error():
            raise ValueError()

        self.assertEqual(5, throw_value_error())

    def test_catching(self):
        def throw_value_error():
            raise ValueError()

        def nop():
            return 4

        self.assertRaises(ValueError, lambda: catch_exception(TypeError, throw_value_error))
        self.assertIsInstance(catch_exception(ValueError, throw_value_error), ValueError)
        self.assertRaises(ValueError, lambda: catch_exception(ValueError, nop))
        self.assertEqual(4, catch_exception(TypeError, nop, return_value_on_no_exception=True))
        self.assertEqual(5, catch_exception(TypeError, nop, return_instead=5))

        self.assertIsInstance(catch_exception((ValueError, TypeError), throw_value_error),
                              ValueError)

    @silence_excs(ValueError)
    def test_silencer_2(self):
        raise ValueError()

    def test_silencer(self):
        with silence_excs(TypeError):
            raise TypeError()

    def test_rethrow(self):
        try:
            with rethrow_as((ValueError, NameError)):
                raise ValueError()
        except NameError:
            return

        self.fail()

    def test_rethrow_3(self):
        try:
            with rethrow_as(ValueError, NameError):
                raise ValueError()
        except NameError:
            return

        self.fail()

    def test_rethrow_2(self):

        @rethrow_as((ValueError, NameError))
        def lol():
            raise ValueError()

        self.assertRaises(NameError, lol)

    def test_issue_10(self):

        class WTFException1(Exception): pass

        class WTFException2(Exception): pass

        @rethrow_as((NameError, WTFException1),
                    (TypeError, WTFException2))
        def provide(exc):
            raise exc()

        self.assertRaises(WTFException1, lambda: provide(NameError))
        self.assertRaises(WTFException2, lambda: provide(TypeError))

    def test_issue_14a(self):

        @rethrow_as(*(((NameError, ValueError), TypeError),))
        def ro(p):
            raise p()

        self.assertRaises(TypeError, lambda: ro(NameError))
        self.assertRaises(TypeError, lambda: ro(ValueError))
        self.assertRaises(RuntimeError, lambda: ro(RuntimeError))

    def test_issue_14b(self):

        @rethrow_as((NameError, ValueError), TypeError)
        def ro(p):
            raise p()

        self.assertRaises(TypeError, lambda: ro(NameError))
        self.assertRaises(TypeError, lambda: ro(ValueError))
        self.assertRaises(RuntimeError, lambda: ro(RuntimeError))
