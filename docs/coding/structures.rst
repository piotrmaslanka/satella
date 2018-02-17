Heap
----

This essentially allows you to have a heap object that will pretty much
behave like the `heapq <https://docs.python.org/2/library/heapq.html>` library.

.. autoclass:: satella.coding.Heap
:members:

TimeBasedHeap
---------

Time-based heap is a good structure if you have many callbacks set to fire at a particular
time in the future. It functions very like a normal Heap.

.. autoclass:: satella.coding.TimeBasedHeap
:members:

typednamedtuple
---------------

It's a named tuple, but it has typed fields. You will get a TypeError if you
try to assign something else there.

.. autofunction:: satella.coding.typednamedtuple
