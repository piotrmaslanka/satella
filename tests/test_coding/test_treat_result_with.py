import logging
import typing
import unittest

from satella.coding import treat_result_with

logger = logging.getLogger(__name__)


class TreatResultWithTest(unittest.TestCase):
    def test_treat_result_with(self):

        @treat_result_with(int)
        def mirror(v):
            return v

        self.assertEquals(mirror('5'), 5)
