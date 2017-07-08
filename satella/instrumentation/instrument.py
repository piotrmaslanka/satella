# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging
import warnings
from satella.coding import Monitor
from satella.coding.debug import typed

logger = logging.getLogger(__name__)

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

class Instrument(object):
    """Class that holds metrics"""

    @typed(object, six.string_types, six.string_types, int)
    def __init__(self, name, description=u'', detail=RUNTIME):
        """
        :param name: system identifier. Separate with dots.
        :param description: human-readable description
        """
        self.name = name
        self.detail = detail
        self.metrics = {}   # name => Metric

    @typed(object, six.string_types, int, int, six.string_types)
    def get_log(self, name, detail, buffer_size=20, description=u''):
        try:
            return self.metrics[name]
        except KeyError:
            from .metrics import StringMetric
            self.metrics[name] = StringMetric(self, name, buffer_size, detail, self.detail, description)
            return self.metrics[name]

    @typed(object, six.string_types, int, six.string_types)
    def get_counter(self, name, detail, description=u''):
        try:
            return self.metrics[name]
        except KeyError:
            from .metrics import CounterMetric
            self.metrics[name] = CounterMetric(self, name, detail, self.detail, description)
            return self.metrics[name]

    @typed(object, int)
    def set_detail(self, detail):
        """
        Set new detail level for all metrics
        :param detail: detail level
        """
        for metric in six.itervalues(self.metrics):
            metric.on_instrument_changed_detail(detail)

        self.detail = detail


class Manager(Monitor):
    """
    There is normally one Manager instance, which holds the entire
    Instrument set
    """
    def __init__(self):
        super(Manager, self).__init__(self)
        self.instruments = {}

    @typed(None, object)
    def __contains__(self, instrument):
        return instrument.name in self.instruments

    @typed(object, six.string_types, six.string_types, int)
    @Monitor.synchronized
    def getInstrument(self, name, description=u'', detail=RUNTIME):
        if name in self.instruments:
            return self.instruments[name]
        else:
            self.instruments[name] = Instrument(name, description, detail)
            return self.instruments[name]


manager = Manager()


@typed(six.string_types, six.string_types, int)
def getInstrument(name, description=u'', detail=RUNTIME):
    return manager.getInstrument(name, description, detail)
