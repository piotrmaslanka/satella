# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging
import time
import monotonic
logger = logging.getLogger(__name__)

from .instrument import Metric
from satella.coding import typed


class StringMetric(Metric):
    """Stores string and their date/time"""

    @typed(object, object, six.string_types, int, int, int, six.string_types)
    def __init__(self, instrument, name, buffer_size, minimum_detail, current_detail, description=u''):
        super(StringMetric, self).__init__(instrument, name, minimum_detail, current_detail, description)

        self.buffer_size = buffer_size
        self.buffer = []    # tuple of (real time, monotonic, string - sorted by timestamp ASC)

    def _log(self, text, *args):
        """Log - as if formatting string"""
        # Nothing to log


        p = time.time(), monotonic.monotonic(), text % args

        while len(self.buffer) >= self.buffer_size:
            del self.buffer[0]

        self.buffer.append(p)

    def view(self):
        """        
        :return: list, sorted by timestamp ASC, or (UNIX timestamp, monotonic time, some string) 
        """
        return self.buffer


class CounterMetric(Metric):
    """
    Counter that counts from beginning (ie. time 0)
    """

    def __init__(self, *args, **kwargs):
        super(CounterMetric, self).__init__(*args, **kwargs)
        self.value = 0
        self.items = 0
        self.sum = 0

    def view(self):
        """:return: a tuple of (current values, times counted, arithmetic mean)
        Mean is NaN if nothing counted"""
        try:
            return self.value, self.items, self.value / self.items
        except ZeroDivisionError:
            self.value, self.items, float('nan')

    def _log(self, delta):
        """Add a value to counter"""
        self.value += delta
        self.items += 1



