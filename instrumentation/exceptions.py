class InstrumentationException(Exception):
    """Root class for instrumentation exceptions"""

class CounterExistsException(InstrumentationException):
    """The counter already exists and cannot be added"""

class NoDataException(InstrumentationException):
    """Data cannot be output as because it isn't there"""