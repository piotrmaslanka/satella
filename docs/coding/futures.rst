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

.. autoclass:: satella.coding.concurrent.futures.ExecutorWrapper
    :members:

3 of the aforementioned modules are also allowed to be imported from `satella.coding.concurrent`,
but that is deprecated! Please import them from `satella.coding.concurrent.futures`.

.. autofunction:: satella.coding.concurrent.futures.call_in_future

.. autofunction:: satella.coding.concurrent.futures.wrap_if

