from satella.instrumentation.basecounter import Counter

class DeltaCounter(Counter):
    """
    A counter that tracks modifications to particular value

    Use like:

        cc = DeltaCounter('a_value')    # value after this call: 0
        cc.update(-1)   # value after this call: -1
        cc.update(+5)   # value after this call: 4
        cc.update(-1.02) # value after this call: 2.98
        ...
    """

    def __init__(self, name, units=None, description=None):
        Counter.__init__(self, name, units=units, description=description)

        self.current_value = 0   #: current value

    def update(self, value):
        """Deltas the counter with given value"""
        if not self.enabled: return
        self.current_value += value

    def get_current(self):
        return self.current_value
