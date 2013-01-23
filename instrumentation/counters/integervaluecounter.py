from time import time

from satella.instrumentation.basecounter import InstrumentationCounter
from satella.instrumentation.exceptions import NoData

class IntegerValueCounter(InstrumentationCounter):
    """A counter that tracks a particular integer value"""

    def __init__(self, name, severity=0):
        InstrumentationCounter.__init__(self, name, severity=severity)

        self.current_value = None   #: current value

        self.history = []   #: list of tuple(time, value)

    def update(self, value):
        """Updates the counter with given value"""
        if not self.enabled: return
        self.history.append((time(), value))
        self.current_value = value

    def get_current(self):
        if self.current_value == None:
            raise NoData, 'No data in the counter'

        return self.current_value
