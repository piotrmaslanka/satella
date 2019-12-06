import logging
import typing as tp
import unittest
import os
import signal
import sys
from satella.instrumentation import install_dump_frames_on
logger = logging.getLogger(__name__)


class TestDumpFramesOn(unittest.TestCase):
    @unittest.skipIf('win' in sys.platform, 'Running on Windows')
    def test_dump_frames_on(self):
        install_dump_frames_on(signal.SIGUSR2)
        os.kill(0, int(signal.SIGUSR2))
