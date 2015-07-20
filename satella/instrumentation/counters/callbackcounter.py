from satella.instrumentation.basecounter import Counter
from satella.instrumentation.exceptions import InstrumentationException, NoData

class CallbackCounter(Counter):
    """A counter whose value is dependent on a function call, ie. computed at runtime

    Let's say that a application has a list object, whose size it would like to keep track of.
    It could call L{satella.instrumentation.counters.DeltaCounter} every time it updates it,
    but that would just be useless.

    Instead, satella provides a CallbackCounter. Each call of get_current is dependent on state
    of particular function call, made at runtime.

    """

    def __init__(self, name, callback, units=None, description=None):
        """
        @param callback: an argumentless callable which returns a value
            that constitutes this counter's value
        @type callback: callable/0
        """
        Counter.__init__(self, name, units=units, description=description)
        self.callback = callback

    def update(self):
        """Deltas the counter with given value"""
        raise InstrumentationException, 'this object does not support update()'

    def get_current(self):
        if not self.enabled:
            raise NoData, 'disabled counter cannot provide data'
        return self.callback()
