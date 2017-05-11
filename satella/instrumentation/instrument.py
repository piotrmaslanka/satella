# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging
from satella.coding import Monitor

logger = logging.getLogger(__name__)


class Instrument(object):
    """Class used for generating metrics"""


    def __init__(self, name):
        self.name = name
        self.ancestry = name.split('.')

    def is_child_of(self, instrument):
        raise NotImplementedError





class Manager(Monitor):
    """
    There is normally one Manager instance, which holds the entire
    Instrument set
    """
    def __init__(self):
        super(Manager, self).__init__(self)
        self.instruments = {}

    @Monitor.synchronized
    def getInstrument(self, name):
        if name in self.instruments:
            return self.instruments[name]
        else:
            self.instruments[name] = Instrument(name)
            return self.instruments[name]


manager = Manager()


def getInstrument(name):
    return manager.getInstrument(name)
