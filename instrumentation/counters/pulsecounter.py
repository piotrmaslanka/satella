from time import time

from satella.instrumentation.counters import BaseCounter

class PulseCounter(BaseCounter):
    """Counter that tracks frequency of calls to update()"""

    def __init__(self, name, resolution=1):
        """
        Creates a new pulse-counting object

        @param resolution: Resolution of the counter in seconds. It will aggregate
            pulses in these periods
        @type resolution: int or float
        """
        BaseCounter.__init__(self, name)
        self.resolution = 1
        self.pulses = []

    def update(self):
        """A single pulse that will be tracked"""
        self.pulses.append(time())

    def get_current(self):
        """Run thru the table"""
        pulses = 0
        stime = time()

        for t in reversed(self.pulses)
            if (stime - t) < resolution:
                pulses += 1
            else:
                break

        del self.pulses[len(self.pulses)-pulses:]    # delete pulses before, they are not relevant

        return pulses