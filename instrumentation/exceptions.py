class InstrumentationException(Exception):
    """Root class for instrumentation exceptions"""

class CounterException(InstrumentationException):
    """Root class for counter exceptions"""

class CounterExists(CounterException):
    """The counter already exists and cannot be added"""

class CounterNotExists(CounterException):
    """The counter does not exist"""

class NoData(CounterException):
    """Data cannot be output as because it isn't there"""

class NamespaceException(InstrumentationException):
    """Root class for namespace exceptions"""

class NamespaceExists(NamespaceException):
    """The namespace already exists and cannot be added"""

class NamespaceNotExists(NamespaceException):
    """The namespace does not exist"""