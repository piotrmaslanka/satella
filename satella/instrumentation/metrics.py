# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging
import time
from satella.resources.memorysensitive import MemorySensitive
import monotonic
logger = logging.getLogger(__name__)

from .instrument import Metric, DISABLED


class StringMetric(Metric, MemorySensitive):
    """Stores string and their date/time"""

    def __init__(self, instrument, name, trigger_level, current_level, description=u'', buffer_size=20):
        Metric.__init__(self, instrument, name, trigger_level, current_level, description=description)
        MemorySensitive.__init__(self)

        self.buffer_size = buffer_size
        self.buffer = []    # tuple of (real time, monotonic, string - sorted by timestamp ASC)

    def on_low_memory_event(self):
        self.buffer = []

    def log(self, text, *args):
        """Log - as if formatting string"""
        # Nothing to log
        if self.current_level < self.trigger_level:
            return

        self.buffer = self.buffer[:-self.buffer_size+1]
        self.buffer.append((
            time.time(),
            monotonic.monotonic(),
            text % args
        ))




