Concurrent data structures
==========================

CallableGroup
-------------

.. autoclass:: satella.coding.concurrent.CallableGroup
    :members:

LockedDataset
-------------

.. autoclass:: satella.coding.concurrent.LockedDataset
    :members:

TerminableThread
----------------

Note that _force=True_ is not available on PyPy. If an attempt to use it on PyPy is made,
``RuntimeError`` will be thrown.

.. autoclass:: satella.coding.concurrent.TerminableThread
    :members:
