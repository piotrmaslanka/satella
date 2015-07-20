from time import time

from satella.instrumentation.basecounter import Counter
from satella.instrumentation.exceptions import NoData

class StringValueCounter(Counter):
    """
    A counter that has a string as its value

    Use like:

        cc = StringValueCounter('test')    # value after the call: None (NoData)
        cc.update('Hello')      # value after the call: 'Hello'
        cc.update('olleH')     # value after the call: 'olleH'

    """

    def __init__(self, name, units=None, description=None, history=0):
        """
        @param history: Maximum amount of history entries cached
        """
        Counter.__init__(self, name, units=units, description=description)

        self.current_value = None   #: current value
        self.history_len = history
        self.history = []   #: list of tuple(time, value)

    def update(self, value):
        """Updates the counter with given value"""
        if not self.enabled: return
        self.history.append((time(), value))
        self.current_value = value

        if len(self.history) > self.history_len:
            del self.history[0]

    def get_current(self):
        if self.current_value == None:
            raise NoData, 'No data in the counter'

        return self.current_value

    def get_history(self):
        return self.history