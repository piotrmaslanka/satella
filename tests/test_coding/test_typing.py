import unittest

from satella.coding.typing import ExceptionClassType


class TestTyping(unittest.TestCase):
    def test_exception_type(self):
        def catch_exception(e) -> ExceptionClassType:
            try:
                e()
            except Exception as e:
                return e.__class__

        a = catch_exception(lambda: hello)
