from satella.instrumentation.basecounter import Counter

class DeltaCounter(Counter):
    """A counter that modifications to particular value"""

    def __init__(self, name, units=None, description=None):
        Counter.__init__(self, name, units=units, description=description)

        self.current_value = 0   #: current value

    def update(self, value):
        """Deltas the counter with given value"""
        if not self.enabled: return
        self.current_value += value

    def get_current(self):
        return self.current_value
