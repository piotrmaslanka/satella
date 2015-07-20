class InstrumentationException(Exception):
    """Root class for instrumentation exceptions"""

class ObjectException(InstrumentationException):
    """Root class for counterobject exceptions"""

class ObjectExists(ObjectException):
    """The counter already exists and cannot be added"""

class ObjectNotExists(ObjectException):
    """The counter does not exist"""

class NoData(InstrumentationException):
    """Data cannot be output as because it isn't there"""