__all__ = ['BaseSatellaException', 'ResourceLockingError', 'ResourceNotLocked', 'ResourceLocked',
           'ConfigurationValidationError', 'ConfigurationError', 'ConfigurationSchemaError',
           'PreconditionError', 'MetricAlreadyExists']


class BaseSatellaException(Exception):
    """"Base class for all Satella exceptions"""
    def __init__(self, msg, *args, **kwargs):
        super().__init__(*(msg, *args))
        self.kwargs = kwargs
        self.msg = msg

    def __str__(self):
        a = '%s(%s' % (self.__class__.__qualname__, self.args)
        if self.kwargs:
            a += ', '+(', '.join(map(lambda k, v: '%s=%s' % (k, repr(v)), self.kwargs.items())))
        a += ')'
        return a

    def __repr__(self):
        a = '%s%s(%s' % ((self.__class__.__module__ + '.')
                         if self.__class__.__module__ != 'builtins' else '',
                         self.__class__.__qualname__,
                         ', '.join(map(repr, self.args)))
        if self.kwargs:
            a += ', ' + (', '.join(map(lambda kv: '%s=%s' % (kv[0], repr(kv[1])),
                                       self.kwargs.items())))
            a += ')'
        return a


class ResourceLockingError(BaseSatellaException):
    """Base class for resource locking issues"""


class ResourceLocked(ResourceLockingError):
    """Given resource has been already locked"""


class ResourceNotLocked(ResourceLockingError):
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

    def __init__(self, msg, value=None, **kwargs):
        """
        :param value: value found
        """
        super().__init__(msg, value, **kwargs)
        self.value = value


class MetricAlreadyExists(BaseSatellaException):
    """Metric with given name already exists, but with a different type"""

    def __init__(self, msg, name, requested_type, existing_type):
        super().__init__(msg)
        self.name = name
        self.requested_type = requested_type
        self.existing_type = existing_type


class LockIsHeld(ResourceLocked):
    """
    An exception raised when lock is held by someone

    :param pid: PID of the holder, who is alive at the time this exception was raised.
        This is checked via psutil.
    """

    def __init__(self, pid):
        self.pid = pid
