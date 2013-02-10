from time import time
from threading import Lock
from collections import defaultdict

from satella.instrumentation.basecounter import CounterObject
from satella.instrumentation.exceptions import ObjectExists, NoData, \
                                               ObjectNotExists

from satella.threads import Monitor

class CounterCollection(Monitor, CounterObject):
    """
    Class used to manage instrumentation counters or their collections

    You can nest counters within collections, and collections within collections.
    There should be a root collection on the stop, that can be fed to presentation
    layer.

    Names inserted should be unique

    This class is threadsafe.
    """
    def __init__(self, namespace, description=None):
        Monitor.__init__(self)
        CounterObject.__init__(self, namespace, description=description)
        self.items = {}

    @Monitor.protect
    def get(self, name):
        if name not in self.items:
            raise ObjectNotExists, 'object not found'
        return self.items[name]

    @Monitor.protect
    def enable(self):
        CounterObject.enable(self)
        for co in self.items.itervalues():
            co.enable()

    @Monitor.protect
    def disable(self):
        CounterObject.disable(self)
        for co in self.items.itervalues():
            co.disable()

    @Monitor.protect
    def add(self, counterobject):
        """
        @param counter: A counterobject to add
        @type counter: descendant of L{CounterObject}

        """
        if counterobject.name in self.items:
            raise ObjectExists, 'already added'

        self.items[counterobject.name] = counterobject
        counterobject._on_added(self)

    @Monitor.protect
    def remove(self, counterobject):
        """
        @param counter: Counterobject to remove. Must exist in this collection.
        @type counter: descendant of L{CounterObject}
        """
        if counterobject.name not in self.items:
            raise ObjectNotExists, 'not in this collection'

        del self.items[counterobject.name]

        counterobject._on_removed()