from time import time

from satella.instrumentation.counters import BaseCounter
from satella.instrumentation.exceptions import NoDataException

class IntegerValueCounter(BaseCounter):
    """A counter that tracks a particular integer value"""

    def __init__(self, name):
        BaseCounter.__init__(self, name)

        self.current_value = None   #: current value

        self.history = []   #: list of tuple(time, value)

    def update(self, value):
        """Updates the counter with given value"""
        self.history.append((time(), value))
        self.current_value = value

    def get_current(self):
        if self.current_value == None:
            raise NoDataException, 'No data in the counter'
            
        return self.current_value
