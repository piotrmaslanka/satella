class InstrumentationException(Exception):
    """Root class for instrumentation exceptions"""

class CounterExists(InstrumentationException):
    """The counter already exists and cannot be added"""

class NoData(InstrumentationException):
    """Data cannot be output as because it isn't there"""