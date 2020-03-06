========================
Functions and decorators
========================

.. autofunction:: satella.coding.merge_dicts

.. autofunction:: satella.coding.static_var

.. autofunction:: satella.coding.silence_excs

.. autoclass:: satella.coding.rethrow_as
    :members:

.. autofunction:: satella.coding.catch_exception

.. autofunction:: satella.coding.for_argument

Now, give the following type structure:

::

    class MetaA(type):
        pass

    class MetaB(type):
        pass

    class A(metaclass=MetaA):
        pass

    class B(metaclass=MetaB):
        pass

You just can't construct the following class

::

    class C(A,B):
        pass

Without running into `TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases`.

Following function will help with that:

.. autofunction:: satella.coding.metaclass_maker

Preconditions
-------------

Sometimes you need to specify conditions that parameter to your function will need to obey.
You can use the following decorator for this:

.. autofunction:: satella.coding.precondition

And here are some helper functions for it:

has_keys asserts that a dictionary has all the keys necessary.

.. autofunction:: satella.coding.has_keys

Use it like this:

>>> @precondition(has_keys(['a', 'b']))
>>> def function(keys):
>>>     ...
>>> function({'a': 5, 'b': 3})
>>> self.assertRaises(PreconditionError, lambda: function({'a': 5}))

short_none is particularly useful with preconditions, or functions
that accept a None value as well.

.. autofunction:: satella.coding.short_none

Example:

>>> @precondition(short_none('x == 2'))
>>> def expect_two(x=None):
>>>     ...
>>> expect_two(None)
>>> expect_two(2)
>>> self.assertRaises(PreconditionError, lambda: expect_two(3))

attach_arguments
----------------

.. autofunction:: satella.coding.attach_arguments

wraps
-----
A ``functools.wraps()`` equivalent, but for classes

.. autofunction:: satella.coding.wraps
