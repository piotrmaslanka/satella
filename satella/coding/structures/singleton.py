# coding=UTF-8
from __future__ import print_function, absolute_import, division

import functools

import six

__all__ = [
    'Singleton',
]

if six.PY3:

    # Taken from https://wiki.python.org/moin/PythonDecoratorLibrary
    def singleton(cls):
        """
        Make a singleton out of decorated class.

        Usage:

            @Singleton
            class MyClass(object):
                ...
        """

        cls.__new_old__ = cls.__new__

        @functools.wraps(cls.__new__)
        def singleton_new(cls, *args, **kw):
            it = cls.__dict__.get('__it__')
            if it is not None:
                return it

            cls.__it__ = it = cls.__new_old__(cls, *args, **kw)
            it.__init_old__(*args, **kw)
            return it

        cls.__new__ = singleton_new
        cls.__init_old__ = cls.__init__
        cls.__init__ = object.__init__

        return cls
else:
    class _SingletonWrapper:
        """
        A singleton wrapper class. Its instances would be created
        for each decorated class.
        """

        def __init__(self, cls):
            self.__wrapped__ = cls
            self._instance = None

        def __call__(self, *args, **kwargs):
            """Returns a single instance of decorated class"""
            if self._instance is None:
                self._instance = self.__wrapped__(*args, **kwargs)
            return self._instance


    # taken from https://pypi.python.org/pypi/singleton-decorator/1.0.0
    def singleton(cls):
        """
        A singleton decorator. Returns a wrapper objects. A call on that object
        returns a single instance object of decorated class. Use the __wrapped__
        attribute to access decorated class directly in unit tests.
        """
        return _SingletonWrapper(cls)

Singleton = singleton
