class BaseSatellaException(Exception):
    def __init__(self, msg, *args, **kwargs):
        super().__init__(*(msg, *args))
        self.msg = msg

    def __str__(self):
        return '%s(%s)' % (self.__class__.__qualname__, self.args)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__qualname__, ', '.join(map(repr, self.args)))


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
        super().__init__(msg, value=value)
        self.value = value
