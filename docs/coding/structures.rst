==========
Structures
==========

The following is a guide to all the data structures that Satella defines.

Heap
====

This essentially allows you to have a heap object that will pretty much
behave like the `heapq <https://docs.python.org/2/library/heapq.html>` library.

.. autoclass:: satella.coding.structures.Heap
    :members:

TimeBasedHeap
=============

Time-based heap is a good structure if you have many callbacks set to fire at a particular
time in the future. It functions very like a normal Heap.

.. autoclass:: satella.coding.structures.TimeBasedHeap
    :members:

typednamedtuple
===============

It's a named tuple, but it has typed fields. You will get a TypeError if you
try to assign something else there.

.. autofunction:: satella.coding.structures.typednamedtuple

OmniHashableMixin
=================

If you need quick __hash__ and __eq__ operators from listed fields of the class.

.. autoclass:: satella.coding.structures.OmniHashableMixin
    :members:

Singleton
=========

Makes the resulting object's ``__init__()`` be called at most once, then caches the object and returns the same
upon each instantiation.

.. autofunction:: satella.coding.structures.Singleton

DictObject
==========

DictObject is an object constructed out of a dict, that allows it's values to be obtained as getattr(), and not only
getitem().

.. autoclass:: satella.coding.structures.DictObject
    :members:

You can use the following function to recursively turn every dict into a DictObject

.. autofunction:: satella.coding.structures.apply_dict_object

