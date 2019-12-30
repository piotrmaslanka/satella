class BaseSatellaException(Exception):
    def __init__(self, msg):
        super(BaseSatellaException, self).__init__()
        self.msg = msg

    def __str__(self):
        return 'BaseSatellaException(%s)' % (repr(self.msg),)


class ResourceLocked(BaseSatellaException):
    """Given resource has been already locked"""


class ResourceNotLocked(BaseSatellaException):
    """Locking given resource is needed in order to access it"""


class PreconditionError(BaseSatellaException, ValueError):
    """
    A precondition was not met for the argument
    """


class ConfigurationError(BaseSatellaException):
    """A generic error during configuration"""


class ConfigurationSchemaError(ConfigurationError):
    """Schema mismatch to what was seen"""


class ConfigurationValidationError(ConfigurationSchemaError):
    """A validator failed"""

    def __init__(self, msg, value=None):
        """
        :param value: value found
        """
        super(ConfigurationValidationError, self).__init__(msg)
        self.value = value
