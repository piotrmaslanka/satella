# coding=UTF-8
from __future__ import print_function, absolute_import, division

import logging

import six

from satella.coding import Monitor, typed
from .metrics import Metric, RUNTIME

logger = logging.getLogger(__name__)

DISABLED = 0
DEBUG = 1
RUNTIME = 2

class InstrumentList(list):
    def __init__(self, children):
        list.__init__(self)
        self.extend(children)

    @typed(object, int)
    def set_detail(self, detail):
        """
        Set new detail level for all instruments in this list
        :param detail: detail level
        """
        for instrument in self:
            instrument.set_detail(detail)


class Instrument(object):
    """Class that holds metrics"""

    @typed(object, six.string_types, six.string_types, int, (None, object))
    def __init__(self, name, description=u'', detail=RUNTIME):
        """
        :param name: system identifier. Separate with dots.
        :param description: human-readable description
        """
        self.name = name
        self.detail = detail
        self.metrics = {}  # name => Metric

    @typed(object, six.string_types, int, int, six.string_types, returns=Metric)
    def get_log(self, name, detail, buffer_size=20, description=u''):
        try:
            return self.metrics[name]
        except KeyError:
            from .metrics import StringMetric
            self.metrics[name] = StringMetric(self, name, buffer_size, detail, self.detail, description)
            return self.metrics[name]

    @typed(object, six.string_types, int, six.string_types, returns=Metric)
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

    @typed(returns=InstrumentList)
    def get_children(self):
        """"
        Get all DIRECT descendenta of this instrument.
        
        Ie if it's called root it will return root.wtf, root.zomg, but not root.wtf.a
        """
        children = []
        basename = self.name + u'.'
        dots = self.name.count(u'.')

        with Monitor.acquire(manager):
            children = [i_name for i_name in manager.instruments if
                        i_name.startswith(basename) and i_name.count(u'.') == dots + 1]
            return InstrumentList(manager.instruments[name] for name in children)


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

    @typed(object, six.string_types, six.string_types, int, returns=Instrument)
    @Monitor.synchronized
    def getInstrument(self, name, description=u'', detail=RUNTIME):
        if name in self.instruments:
            return self.instruments[name]
        else:
            self.instruments[name] = Instrument(name, description, detail)
            return self.instruments[name]


manager = Manager()


@typed(six.string_types, six.string_types, int, returns=Instrument)
def getInstrument(name, description=u'', detail=RUNTIME):
    return manager.getInstrument(name, description, detail)
