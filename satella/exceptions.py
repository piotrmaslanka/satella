import warnings
import typing as tp

__all__ = ['BaseSatellaError', 'ResourceLockingError', 'ResourceNotLocked', 'ResourceLocked',
           'ConfigurationValidationError', 'ConfigurationError', 'ConfigurationSchemaError',
           'PreconditionError', 'MetricAlreadyExists', 'BaseSatellaException', 'CustomException',
           'CodedCustomException', 'CodedCustomExceptionMetaclass', 'WouldWaitMore', 'LockIsHeld',
           'ProcessFailed']


class CustomException(Exception):
    """"
    Base class for your custom exceptions. It will:

    1. Accept any number of arguments
    2. Provide faithful __repr__ and a reasonable __str__

    It passed all arguments that your exception received via super().
    Just remember to actually pass these arguments in your inheriting classes!
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.kwargs = kwargs

    def __str__(self) -> str:
        a = '%s(%s' % (self.__class__.__qualname__.split('.')[-1], ', '.join(map(repr, self.args)))
        if self.kwargs:
            a += ', ' + ', '.join(map(lambda k, v: '%s=%s' % (k, repr(v)), self.kwargs.items()))
        a += ')'
        return a

    def __repr__(self) -> str:
        a = '%s%s(%s' % ((self.__class__.__module__ + '.')
                         if self.__class__.__module__ != 'builtins' else '',
                         self.__class__.__qualname__,
                         ', '.join(map(repr, self.args)))
        if self.kwargs:
            a += ', ' + (', '.join(map(lambda kv: '%s=%s' % (kv[0], repr(kv[1])),
                                       self.kwargs.items())))
        a += ')'
        return a


def get_base_of_bases(classes):
    class_bases = ()
    for class_ in classes:
        class_bases += class_.__bases__
    return class_bases


class CodedCustomExceptionMetaclass(type):
    """
    Metaclass implementing the isinstance check for coded custom exceptions
    """
    code = None     # type: tp.Optional[tp.Any]

    def __instancecheck__(cls, instance):
        if super().__instancecheck__(instance):
            return True

        if cls is CodedCustomException:
            return super().__instancecheck__(instance)

        class_base = (cls, )
        while CodedCustomException not in get_base_of_bases(class_base) and class_base:
            class_base = get_base_of_bases(class_base)

        inst_base = (instance.__class__, )
        while CodedCustomException not in get_base_of_bases(inst_base) and inst_base:
            inst_base = get_base_of_bases(inst_base)

        if len(set(class_base).intersection(set(inst_base))) == 0:
            # These classes belong in different exception hierarchies
            return False

        try:
            return cls.code == instance.code
        except AttributeError:
            return super().__instancecheck__(instance)


class CodedCustomException(CustomException, metaclass=CodedCustomExceptionMetaclass):
    def __init__(self, message, code=None, *args, **kwargs):
        super().__init__(message, code, *args, **kwargs)
        self.message = message      # type: str
        if code is not None:
            self.code = code


class BaseSatellaError(CustomException):
    """"Base class for all Satella exceptions"""


class BaseSatellaException(BaseSatellaError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        warnings.warn('Use BaseSatellaError instead', DeprecationWarning)


class ResourceLockingError(BaseSatellaError):
    """Base class for resource locking issues"""


class ResourceLocked(ResourceLockingError):
    """Given resource has been already locked"""


class ResourceNotLocked(ResourceLockingError):
    """Locking given resource is needed in order to access it"""


class WouldWaitMore(ResourceLockingError, TimeoutError):
    """wait()'s timeout has expired"""


class PreconditionError(BaseSatellaError, ValueError):
    """
    A precondition was not met for the argument
    """


class ConfigurationError(BaseSatellaError, ValueError):
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


class MetricAlreadyExists(BaseSatellaError):
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
        super().__init__(pid)
        self.pid = pid


class ProcessFailed(BaseSatellaError, OSError):
    """A process finished with other result code that it was requested

    :param rc: return code of the process
    :param stdout_so_far: process' stdout gathered so far
    """

    def __init__(self, rc: int, stdout_so_far: tp.Union[bytes, str]):
        super().__init__(rc, stdout_so_far)
        self.rc = rc
        self.stdout_so_far = stdout_so_far

    def __str__(self):
        return 'ProcessFailed(%s)' % (self.rc, )
