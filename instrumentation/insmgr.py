from time import time
from threading import Lock

from satella.instrumentation.basecounter import InstrumentationCounter
from satella.instrumentation.exceptions import CounterExists, NoData, \
                                               CounterNotExists
from satella.instrumentation.snapshots import CountersSnapshot
from satella.threads import Monitor

class InstrumentationManager(Monitor):
    """
    Class used to manage instrumentation counters.

    There can exist many L{InstrumentationManager} classes, each with own set 
    of instrumentation counters - with different namespace names. You could use
    it if you have multiple output targets, or incredibly large set of counters
    that are specific to a given task. Still, you could prefix instrumentation
    counters with a string to differ them, but that task could be tedious and
    make your app's instrumentation buggy. 

    This class is threadsafe.
    """
    def __init__(self, namespace):
        Monitor.__init__(self)
        self.counters = {}  #: dict(name => (InstrumentationCounter, severity))
        self.namespace = namespace
        self.severity = float('-inf')   #: current severity level

    @Monitor.protect
    def set_severity(self, severity):
        if severity > self.severity:
            # Raising required severity level
            for counter in self.counters.itervalues():
                if counter.severity < severity:
                    counter.disable()
        else:
            # Lowering required severity level
            for counter in self.counters.itervalues():
                if counter.severity >= severity:
                    counter.enable()

        self.severity = severity

    @Monitor.protect
    def add_counter(self, counter):
        """
        @param counter: A counter to register for this instrumentation manager
        @type counter: descendant of L{InstrumentationCounter}

        """
        if counter.name in self.counters:
            raise CounterExists, 'Counter already exists'

        self.counters[counter.name] = counter
        counter._on_added(self)

    @Monitor.protect
    def remove_counter(self, counter):
        """
        @param counter: Counter to be removed from this manager. Must exist
            in this manager
        @type counter: descendant of L{InstrumentationCounter}
        """
        if counter.name not in self.counters:
            raise CounterNotExists
        del self.counters[counter.name]
        counter._on_removed()