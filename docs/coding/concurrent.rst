==========================
Concurrent data structures
==========================

CallableGroup
=============

.. autoclass:: satella.coding.concurrent.CallableGroup
    :members:

LockedDataset
=============

.. autoclass:: satella.coding.concurrent.LockedDataset
    :members:

TerminableThread
================

Note that _force=True_ is not available on PyPy. If an attempt to use it on PyPy is made,
``RuntimeError`` will be thrown.

Please note that in order to terminate, target Python thread must at least execute some Python code.
It means that if it's hanging on I/O, for example, it won't be affected.

.. autoclass:: satella.coding.concurrent.TerminableThread
    :members:
