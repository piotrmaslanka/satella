import logging
import sys
import unittest

from satella.instrumentation.dump_frames_on import dump_frames_on

logger = logging.getLogger(__name__)


class TestDumpFramesOn(unittest.TestCase):
    def test_dump_frames_on(self):
        dump_frames_on(0, None, sys.stderr)
