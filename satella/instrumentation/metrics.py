# coding=UTF-8
from __future__ import print_function, absolute_import, division

import time

import monotonic
import six

from satella.coding import typed

# Detail levels
DISABLED = 0
RUNTIME = 1
DEBUG = 2


class Metric(object):
    """
    Base metric class.

    All metrics have a minimum level. They will not log if their instrument is below this level.

    If this should not log (ie. instrument has lesser level than metric), then self.log will be 
    substituted with an empty function - so pretty fast
    """

    @typed(object, object, six.string_types, int, int, six.string_types)
    def __init__(self, instrument, name, minimum_detail, current_detail, description=u''):
        assert minimum_detail in (DISABLED, RUNTIME, DEBUG)

        self.instrument = instrument
        self.name = name
        self.minimum_detail = minimum_detail
        self.on_instrument_changed_detail(current_detail)

    @typed(object, int)
    def on_instrument_changed_detail(self, new_detail):
        """Our instrument has just changed detail"""
        if new_detail >= self.minimum_detail:
            self.log = self._log
        else:
            self.log = lambda *args, **kwargs: None

    def _log(self, *args, **kwargs):
        """
        This function does real logging. Override it.
        """
        raise NotImplementedError('Override me')

    def view(self):
        """
        Return, quickly and non-blockingly, contents
        :return: depends on metric
        """
        raise NotImplementedError('Override me')


class StringMetric(Metric):
    """Stores string and their date/time"""

    @typed(object, object, six.string_types, int, int, int, six.string_types)
    def __init__(self, instrument, name, buffer_size, minimum_detail, current_detail, description=u''):
        super(StringMetric, self).__init__(instrument, name, minimum_detail, current_detail, description)

        self.buffer_size = buffer_size
        self.buffer = []  # tuple of (real time, monotonic, string - sorted by timestamp ASC)

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

    @typed(returns=tuple)
    def view(self):
        """:return: a tuple of (current values, times counted, arithmetic mean)
        Mean is NaN if nothing counted"""
        try:
            return self.value, self.items, self.value / self.items
        except ZeroDivisionError:
            return 0, 0, float('nan')

    def _log(self, delta):
        """Add a value to counter"""
        self.value += delta
        self.items += 1
