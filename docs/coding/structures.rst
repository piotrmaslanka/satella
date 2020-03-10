==========
Structures
==========

The following is a guide to all the data structures that Satella defines.

Heap
====

This essentially allows you to have a heap object that will pretty much
behave like the heapq_ library.

.. _heapq: https://docs.python.org/2/library/heapq.html

.. autoclass:: satella.coding.structures.Heap
    :members:

SetHeap
=======

A heap with additional invariant that no two elements on the heap are the same.
This is optimized for fast pushes() and membership checks.

.. autoclass:: satella.coding.structures.SetHeap
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

SingletonWithRegardsTo
======================

Sometimes you just need an almost-singleton class, ie. class whose
instance will depend on first *n* arguments. This function makes it easy:

.. autofunction:: satella.coding.structures.SingletonWithRegardsTo

It will remember instances already created and return you a previously
created instance, keying on the first *n* arguments.

DictObject
==========

DictObject is an object constructed out of a dict, that allows it's values to be obtained as getattr(), and not only
getitem().

.. autoclass:: satella.coding.structures.DictObject
    :members:

You can use the following function to recursively turn every dict into a DictObject

.. autofunction:: satella.coding.structures.apply_dict_object

Immutable
=========

Make your classes immutable. Normal assignment is only supported in the constructor,
anywhere else it's a TypeError.

Immutable inherits from abc.ABCMeta, so it's safe to use abstract base classes here.

::

    class Test(Immutable, metaclass=ABCMeta):

        attr: str = None

        def __init__(self):
            self.attr = 'value'

        def illegal_op(self):
            self.attr = 'test'  # this will TypeError

frozendict
==========

A dictionary that can't be modified. I didn't import the one from _frozendict PyPI package,
because it failed on Python 3.9.
It is additionally hashable and __eq__-able

.. _frozendict: https://pypi.org/project/frozendict/

.. autoclass:: satella.coding.structures.frozendict

DictionaryView
==============

.. autoclass:: satella.coding.structures.DictionaryView
    :members:

HashableWrapper
===============

.. autofunction:: satella.coding.structures.HashableWrapper
