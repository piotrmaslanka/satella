class ChannelException(Exception):
    """Base class for channel exceptions"""

class ChannelClosed(ChannelException):
    """Cannot perform this op - channel is closed"""

class ChannelFailure(ChannelException):
    """The channel has failed, operation cannot be completed.
    Channel should be subject to teardown now"""

class UnderlyingFailure(UnderlyingFailure):
    """Cannot perform this op - underlying implementation call failed"""

class DataNotAvailable(ChannelException):
    """Data not yet available"""

class InvalidOperation(ChannelException):
    """This operation is invalid"""

class TransientFailure(ChannelException):
    """Wait for some time and retry the operation"""