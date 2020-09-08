========================
Functions and decorators
========================

.. autofunction:: satella.coding.source_to_function

.. autofunction:: satella.coding.queue_iterator

.. autofunction:: satella.coding.update_key_if_not_none

.. autofunction:: satella.coding.update_attr_if_none

.. autofunction:: satella.coding.merge_dicts

.. autofunction:: satella.coding.static_var

.. autofunction:: satella.coding.silence_excs

.. autoclass:: satella.coding.log_exceptions

.. autoclass:: satella.coding.rethrow_as
    :members:

.. autofunction:: satella.coding.catch_exception

.. autofunction:: satella.coding.raises_exception

.. autofunction:: satella.coding.for_argument

.. autofunction:: satella.coding.chain_functions

.. autofunction:: satella.coding.auto_adapt_to_methods

Wrapping classes with something
-------------------------------

Sometimes you need to wrap all methods/properties in given class with
a common decorator. Here's the function you can use:

.. autofunction:: satella.coding.wrap_with

In order to more easily construct functions that will wrap properties,
the following was provided:

.. autofunction:: satella.coding.wrap_property

You can also decorate given callables in order not to be wrapped with

.. autofunction:: satella.coding.dont_wrap

Function overloading
--------------------

.. autoclass:: satella.coding.overload
    :members:

DocsFromParent
--------------

.. autofunction:: satella.coding.DocsFromParent

CopyDocsFrom
------------

.. autofunction:: satella.coding.CopyDocsFrom

metaclass_maker
---------------

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

Preconditions and postconditions
--------------------------------

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
>>> def expect_two(x):
>>>     ...
>>> expect_two(None)
>>> expect_two(2)
>>> self.assertRaises(PreconditionError, lambda: expect_two(3))

You can also check the return value with

.. autofunction:: satella.coding.postcondition


attach_arguments
----------------

.. autofunction:: satella.coding.attach_arguments

wraps
-----
A ``functools.wraps()`` equivalent, but for classes

.. autofunction:: satella.coding.wraps

execute_before
--------------

.. autofunction:: satella.coding.decorators.execute_before

