from satella.instrumentation.basecounter import InstrumentationCounter
from satella.instrumentation.exceptions import CounterExists

class InstrumentationManager(object):
    """
    Class used to manage instrumentation counters.

    There can exist many L{RootInstrumentation} classes, each with own set of instrumentation
    counters. You could use it if you have multiple output targets, or incredibly large 
    set of counters that are specific to a given task. Still, you could prefix instrumentation
    counters with a string to differ them, but that task could be tedious and make your
    app's instrumentation buggy. 

    Not threadsafe.
    """
    def __init__(self, namespace):
        self.counters = {}  #: dict(name => InstrumentationCounter)
        self.namespace = namespace

    def add_counter(self, counter):
        """
        @param counter: A counter to register for this instrumentation manager
        @type counter: descendant of L{InstrumentationCounter}
        """
        if counter.name in self.counters:
            raise CounterExists, 'Counter already exists'

        self.counters[counter.name] = counter
        counter._on_added()