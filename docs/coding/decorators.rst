Decorators
==========

.. autofunction:: satella.coding.decorators.retry

.. autofunction:: satella.coding.decorators.memoize

.. autofunction:: satella.coding.decorators.queue_get

.. autofunction:: satella.coding.decorators.copy_arguments

.. autofunction:: satella.coding.decorators.loop_while

.. autofunction:: satella.coding.for_argument

.. autofunction:: satella.coding.chain_functions

.. autofunction:: satella.coding.auto_adapt_to_methods

.. autofunction:: satella.coding.attach_arguments

A ``functools.wraps()`` equivalent, but for classes

.. autofunction:: satella.coding.wraps

.. autofunction:: satella.coding.decorators.execute_before

.. autofunction:: satella.coding.decorators.return_as_list


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

