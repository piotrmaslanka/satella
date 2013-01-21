from time import time

from satella.instrumentation.basecounter import InstrumentationCounter

class PulseCounter(InstrumentationCounter):
    """Counter that tracks frequency of calls to update()"""

    def __init__(self, name, resolution=1):
        """
        Creates a new pulse-counting object

        @param resolution: Resolution of the counter in seconds. It will aggregate
            pulses in these periods
        @type resolution: int or float
        """
        InstrumentationCounter.__init__(self, name)
        self.resolution = resolution
        self.pulses = []

    def update(self):
        """A single pulse that will be tracked"""
        if not self.enabled: return
        self.pulses.append(time())

    def get_current(self):
        """Run thru the table"""
        pulses = 0
        stime = time()

        for t in reversed(self.pulses):
            if (stime - t) < self.resolution:
                pulses += 1
            else:
                break

        del self.pulses[len(self.pulses)-pulses:]    # delete pulses before, they are not relevant

        return pulses