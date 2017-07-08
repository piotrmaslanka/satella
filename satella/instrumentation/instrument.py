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
    Base metric class
    """

    @typed(None, Instrument, six.string_types, int, six.string_types)
    def __init__(self, instrument, name, trigger_level, current_level, description=u''):
        self.instrument = instrument
        self.name = name
        self.trigger_level = trigger_level
        self.current_level = current_level
        self.detail = DISABLED

    @typed(None, int)
    def set_detail(self, detail):
        self.detail = detail

class Instrument(object):
    """Class that holds metrics"""

    @typed(None, six.string_types, six.string_types)
    def __init__(self, name, description=u''):
        """
        :param name: system identifier. Separate with dots.
        :param description: human-readable description
        """
        self.name = name
        ancestor_name = u'.'.join(name.split(u'.')[:-1])

        if not ancestor_name in manager:
            warnings.warn(u'Ancestor of %s not found, creating it manually' % (name, ))
            manager.getInstrument(ancestor_name)

        self.detail = ESSENTIAL
        self.metrics = {}   # name => Metric

    @typed(None, int)
    def set_detail(self, detail):
        """
        Set new detail level for all metrics
        :param detail: detail level
        """
        for metric in self.metrics:
            self.set_detail(detail)
        self.detail = detail

    def is_child_of(self, instrument):
        """
        Is this instrument a child instrument of some other?
        :param instrument: Instrument to check
        :return: bool
        """
        return self.name.startswith(instrument.name) and instrument.name[len(self.name)] == u'.'



class Manager(Monitor):
    """
    There is normally one Manager instance, which holds the entire
    Instrument set
    """
    def __init__(self):
        super(Manager, self).__init__(self)
        self.instruments = {}

    @typed(None, Instrument)
    def __contains__(self, instrument):
        return instrument.name in self.instruments

    @typed(None, six.string_types)
    @Monitor.synchronized
    def getInstrument(self, name):
        if name in self.instruments:
            return self.instruments[name]
        else:
            self.instruments[name] = Instrument(name)
            return self.instruments[name]


manager = Manager()

@typed(six.string_types)
def getInstrument(name):
    return manager.getInstrument(name)
