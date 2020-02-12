import io
import logging
import unittest

from satella.instrumentation.dump_frames_on import dump_frames_on

logger = logging.getLogger(__name__)


class TestDumpFramesOn(unittest.TestCase):
    def test_dump_frames_on(self):
        io_out = io.StringIO()
        dump_frames_on(0, None, io_out)
        data = io_out.getvalue()
        self.assertIn('test_dump_frames_on', data)
