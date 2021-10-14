=======================
Exceptions and warnings
=======================

For you to use
==============

Warnings
--------

.. autoclass:: satella.warnings.ExperimentalWarning

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

The CodedCustomException uses the following metaclass to accomplish
it's magic

.. autoclass:: satella.exceptions.CodedCustomExceptionMetaclass
    :members:

ImpossibleError
~~~~~~~~~~~~~~~

.. autoclass:: satella.exceptions.ImpossibleError
    :members:

Note that `ImpossibleError` inherits from `BaseException` instead of the standard Satella hierarchy.
The thought is, since this is an anomalous exception, it should get to the top of the stack ASAP.

Satella-specific exceptions
---------------------------

BaseSatellaError
~~~~~~~~~~~~~~~~

.. autoclass:: satella.exceptions.BaseSatellaError
    :members:


ResourceLockingError
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: satella.exceptions.ResourceLockingError
    :members:


ResourceLocked
~~~~~~~~~~~~~~

.. autoclass:: satella.exceptions.ResourceLocked
    :members:


ResourceNotLocked
~~~~~~~~~~~~~~~~~

.. autoclass:: satella.exceptions.ResourceNotLocked
    :members:


WouldWaitMore
~~~~~~~~~~~~~

.. autoclass:: satella.exceptions.WouldWaitMore
    :members:


PreconditionError
~~~~~~~~~~~~~~~~~

.. autoclass:: satella.exceptions.PreconditionError
    :members:


ConfigurationError
~~~~~~~~~~~~~~~~~~

.. autoclass:: satella.exceptions.ConfigurationError
    :members:


ConfigurationSchemaError
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: satella.exceptions.ConfigurationSchemaError
    :members:


ConfigurationMisconfiguredError
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: satella.exceptions.ConfigurationMisconfiguredError
    :members:

ConfigurationValidationError
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: satella.exceptions.ConfigurationValidationError
    :members:

Empty
~~~~~

.. autoclass:: satella.exceptions.empty
    :members:

MetricAlreadyExists
~~~~~~~~~~~~~~~~~~~

.. autoclass:: satella.exceptions.MetricAlreadyExists
    :members:


AlreadyAllocated
~~~~~~~~~~~~~~~~

.. autoclass:: satella.exceptions.AlreadyAllocated
    :members:


ProcessFailed
~~~~~~~~~~~~~

.. autoclass:: satella.exceptions.ProcessFailed
    :members:


NotEnoughBytes
~~~~~~~~~~~~~~

.. autoclass:: satella.exceptions.NotEnoughBytes
    :members:
