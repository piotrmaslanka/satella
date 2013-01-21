from satella.instrumentation.basecounter import InstrumentationCounter

class DeltaCounter(InstrumentationCounter):
    """A counter that modifications to particular value"""

    def __init__(self, name):
        InstrumentationCounter.__init__(self, name)

        self.current_value = 0   #: current value

    def update(self, value):
        """Deltas the counter with given value"""
        if not self.enabled: return
        self.current_value += value

    def get_current(self):
        return self.current_value
