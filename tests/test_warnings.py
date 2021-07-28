import unittest
import warnings

from satella.warnings import ExperimentalWarning


class TestWarning(unittest.TestCase):
    def test_experimental_warning(self):
        warnings.warn('Experimental', ExperimentalWarning)
