"""
Module supporting counter snapshots
"""
from satella.instrumentation.exceptions import CounterNotExists, NoData

class CountersSnapshot(object):
    """
    A snapshot of counter values in a specific time period
    """

    def __init__(self, cntrdict, stime, insmgr):
        """
        Create a counter snapshot

        @param cntrdict: dictionary of counter_name => counter_value
        @type cntrdict: dict
        @param stime: time of snapshot
        @type stime: int
        @param insmgr: parent InstrumentationManager
        @type insmgr: L{satella.instrumentation.insmgr.InstrumentationManager}
        """
        self.snapshot_time = stime
        self._data = cntrdict
        self._insmgr = insmgr

    def __getitem__(self, key):
        try:
            if self._data[key] == NoData:
                raise NoData, 'no data for %s' % key
            else:
                return self._data[key]
        except KeyError:
            raise CounterNotExists, 'counter %s does not exist' % key
