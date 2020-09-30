==========================
Concurrent data structures
==========================

CallableGroup
=============

.. autoclass:: satella.coding.concurrent.CallableGroup
    :members:

CallNoOftenThan
---------------

.. autoclass:: satella.coding.concurrent.CallNoOftenThan
    :members:

LockedDataset
=============

.. autoclass:: satella.coding.concurrent.LockedDataset
    :members:

TerminableThread
================

Note that **force=True** is not available on PyPy. If an attempt to use it on PyPy is made,
``RuntimeError`` will be thrown.

Please note that in order to terminate, target Python thread must at least execute some Python code.
It means that if it's hanging on I/O, for example, it won't be affected.

.. autoclass:: satella.coding.concurrent.TerminableThread
    :members:

BogusTerminableThread
=====================

.. autoclass:: satella.coding.concurrent.BogusTerminableThread
    :members:

call_in_separate_thread
=======================

.. autofunction:: satella.coding.concurrent.call_in_separate_thread


SingleStartThread
=================

.. autoclass:: satella.coding.concurrent.SingleStartThread
    :members:

IDAllocator
===========

.. autoclass:: satella.coding.concurrent.IDAllocator
    :members:

Monitor
=======

A monitor is a Java-like synchronization idea. Inheriting from Monitor outfits the class with a Lock
(or a reentrant lock, if *RMonitor* is used), that can be used to coordinate access to some shared resource.

Take care to invoke Monitor's constructor when inheriting, or this won't work.

You can decorate your methods with *Monitor.synchronized* to have them execute with the lock acquired.
If you have such a method, you can also temporarily release the lock using context manager  *Monitor.release*
(it will be reacquired) when context manager is exited.

You can also use manual synchronization with context manager *Monitor.acquire*.

::

    from satella.coding import Monitor


    class MyProtectedClass(Monitor):
        def __init__(self, *args):
            super(Monitor, self).__init__()

        @Monitor.synchronized
        def synchronized(self):
            pass # everything here is executed with class lock acquired

        @Monitor.synchronized
        def temporary_release(self):
            pass    # lock is acquired here
            with Monitor.release(self):
                pass    # lock is NOT ACQUIRED here
            pass # and here it's reacquired again

        def manual_sync(self):
            pass    # not synchronized
            with Monitor.acquire(self):
                pass # synchronized


You can also use *Monitor.release* and *Monitor.acquire* with other objects than self, but exercise
caution and think over the consequences.

.. autoclass:: satella.coding.concurrent.Monitor
    :members:

.. autoclass:: satella.coding.concurrent.RMonitor

Additionally, following types are predefined for your convenience:

.. autoclass:: satella.coding.concurrent.MonitorList

.. autoclass:: satella.coding.concurrent.MonitorDict

LockedStructure
===============

A proxy to an object along with a lock, that can be triggered
using the context manager:

::

    a = {1:2, 3:4}
    ls = LockedStructure(a)

    assert len(ls), 2
    with ls:
        a[4] = 5

.. autoclass:: satella.coding.concurrent.LockedStructure

AtomicNumber
============

.. autoclass:: satella.coding.concurrent.AtomicNumber
    :members:

Condition
=========

A simplified version of threading.Condition. Doesn't require you to acquire it
in order to be notified. Just a bunch of syntactic sugar.

.. autoclass:: satella.coding.concurrent.Condition
    :members:

Timer
=====

.. autoclass:: satella.coding.concurrent.Timer
    :members:

Functions and decorators
========================

parallel_execute
----------------

For executing those functions that return a Future in parallel.

parallel_execute will return you an iterator, returning the result
(or raising an exception) for every result you get.

.. autofunction:: satella.coding.concurrent.parallel_execute

run_as_future
-------------

.. autofunction:: satella.coding.concurrent.run_as_future

sync_threadpool
---------------

.. autofunction:: satella.coding.concurrent.sync_threadpool
