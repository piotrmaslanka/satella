==================
Exception handling
==================

Satella provides a rich functionality to register exception hooks.

.. note:: Satella does not install a custom faulthandler_. Do it yourself.

.. _faulthandler: https://docs.python.org/3/library/faulthandler.html

Writing your own exception handlers
===================================

To write your own exception handlers, subclass the following class:

.. autoclass:: satella.exception_handling.BaseExceptionHandler
    :members:

And then instantiate it and call ``install()``.

If you got a callable of signature [type, BaseException, types.TracebackType] (type, value, traceback) that
returns True upon a request to swallow the exception, you can convert it to a Satella exception handler in two ways.

First:

::

    a = FunctionExceptionHandler(exception_handle)
    a.install()

Or

::

    @exception_handler
    def exception_handle(type, value, traceback) -> bool
        ...

    exception_handle().install()

.. autofunction:: satella.exception_handling.exception_handler

.. autoclass:: satella.exception_handling.FunctionExceptionHandler
    :members:

Pre-defined exception handlers
==============================

MemoryErrorExceptionHandler
---------------------------

.. autoclass:: satella.exception_handling.MemoryErrorExceptionHandler

This exception hook kills the entire process if a `MemoryError` is spotted, under the rule that it's better to fail
early than admit undefined behaviour.

DumpToFileHandler
-----------------

.. autoclass:: satella.exception_handling.DumpToFileHandler

A handler that will dump each stack frame of the exception, along with it's variables, to a file (or stdout/stderr).
Two file handles/names are admitted:

* **human_readables** - where human-readable form of the exception and it's values will be output
* **trace_pickles** - where pickled `Traceback`s from the exception will be put.

You can throw there either:

* a **str** - file of given name will be created and data will be output to it
* a file-like object supporting ``write()`` (and optionally ``flush()``) - data will be output to it
* a None - output will be piped to /dev/null

Note that the arguments are lists, so you can specify multiple target sources.


