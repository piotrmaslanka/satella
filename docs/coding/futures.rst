=======
Futures
=======

Satella contains a powerful interface to simplify writing Futures and enable the user
to use functional-style code is a much simpler way.

Improved Futures
----------------

Satella presents the user with Future's that can register callbacks that will change
it's value before returning it to waiting consumers. These futures are normal
Python futures in their own right, and can be wait'ed upon.

.. autoclass:: satella.coding.concurrent.futures.Future
    :members:

.. autoclass:: satella.coding.concurrent.futures.WrappingFuture
    :members:

.. autoclass:: satella.coding.concurrent.futures.InvalidStateError
    :members:

These modules are also allowed to be imported from `satella.coding.concurrent`,
but that is deprecated!

.. autofunction:: satella.coding.concurrent.futures.call_in_future

