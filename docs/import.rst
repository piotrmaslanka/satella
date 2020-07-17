======
Import
======

Sometimes you just have a fairly nested module hierarchy,
and you want to import everything. Don't worry, Satella's got
you covered. Just use this function

.. autofunction:: satella.imports.import_from

An example use would be your module's __init__.py containing
following code:

::

    from satella.imports import import_from

    __all__ = []

    import_from(__path__, __name__, __all__, locals())

In this case, everything will be accessible from this module.
This will examine the __all__ of your submodules, and dir() it
if __all__'s not available. Note that lack of availability of
__all__ will emit a log warning.

And sometimes you just need a particular class loaded, identified
by a module path and class name, eg. ``subprocess.Popen``.
You can use the following function to get it:

.. autofunction:: satella.imports.import_class
