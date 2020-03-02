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
