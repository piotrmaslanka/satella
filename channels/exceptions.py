class ChannelException(Exception):
    """Base class for channel exceptions"""


class FatalException(Exception):
    """Error is non-recoverable"""

class NonfatalException(Exception):
    """Error is recoverable"""    

class ChannelClosed(ChannelException, FatalException):
    """Cannot perform this op - channel is closed"""

class ChannelFailure(ChannelException, FatalException):
    """The channel has failed, operation cannot be completed.
    Channel should be subject to teardown now"""

class UnderlyingFailure(UnderlyingFailure, FatalException):
    """Cannot perform this op - underlying implementation call failed"""

class DataNotAvailable(ChannelException, NonfatalException):
    """Data not yet available"""

class InvalidOperation(ChannelException, FatalException):
    """This operation is invalid"""

class TransientFailure(ChannelException, NonfatalException):
    """Wait for some time and retry the operation"""