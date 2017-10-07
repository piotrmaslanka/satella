Heap
----

This essentially allows you to have a heap object that will pretty much
behave like the `heapq https://docs.python.org/2/library/heapq.html` library.

.. autoclass:: satella.coding.Heap

TimerHeap
---------

Timer heap is a good structure if you have many callbacks set to fire at a particular
time in the future. It bases off Heap.

.. autoclass:: satella.coding.TimerHeap
