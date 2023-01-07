Sometimes, you have a bunch of arguments to functions
such as the database connection object, and would
prefer them not to be passed by an argument, but configured
through Satella's Environments themselves:

.. autoclass:: satella.coding.Context
    :members:

You can think of them as a stack of cards each carrying a set of variable names. The variable, if not present
on the current card, will be checked upwards for parent of this card. Each thread, by default, gets a
separate hierarchy. Removing a variable on one card will not affect it's parent, however the variable will remain
inaccessible for the duration of this context. Use them like this:

.. code-block:: python

    with Context() as ctxt:
        ctxt.value = 55
        with Context() as new_ctxt:
            new_ctxt.value = 66
            assert ctxt.value == 66
        assert ctxt.value == 55
