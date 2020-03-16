Exceptions
==========

CustomException
---------------

This is the class you can base your exceptions off. It provides
a reasonable __repr__ and __str__, eg.:

::

    class MyException(CustomException):
        ...

    assert str(MyException) == 'MyException()'

__repr__ will additionally prefix the exception class name with entire module path to it.

CodedCustomException
--------------------

A CustomException with an additional field in constructor, namely the
exception's code, and a special property that it's subclasses who define
a class property code are considered instances of that class, if it's code matches.

Example:

::

    class BaseCodedError(CodedCustomException):
        def __init__(self, msg, code):
            super().__init__(msg, code)

    class Code2Error(BaseCodedError):
        code = 2

    assert isinstance(BaseCodedError('message', 2', Code2Error)

The exceptions have to be in a common hierarchy to check them via
codes.


For example, the following is true:

::
    class DifferentHierarchy(CodedCustomException):
        pass

    assert not isinstance(DifferentHierarchy('message', 2), Code2Error)


In general, please do not construct direct exceptions from CodedCustomException,
please do it via a hierarchy such as:

::

    class GenericError(CodedCustomException):
        pass

    class SpecificError(GenericError):
        code = 3

    raise SpecificError('message')


Note that this won't allow you to handle exceptions like that

::

    try:
        raise BaseCodedError('message', 2')
    except Code2Error:
        self.succeed()
    else:
        self.fail()

As this is a Python limitation.
