==========
Structures
==========

SparseMatrix
------------

.. autoclass:: satella.coding.structures.SparseMatrix
    :members:


Heaps
=====

Heap
----

This essentially allows you to have a heap object that will pretty much
behave like the heapq_ library.

.. _heapq: https://docs.python.org/2/library/heapq.html

.. autoclass:: satella.coding.structures.Heap
    :members:

SetHeap
-------

A heap with additional invariant that no two elements on the heap are the same.
This is optimized for fast pushes() and membership checks.

.. autoclass:: satella.coding.structures.SetHeap
    :members:


TimeBasedHeap
-------------

Time-based heap is a good structure if you have many callbacks set to fire at a particular
time in the future. It functions very like a normal Heap.

.. autoclass:: satella.coding.structures.TimeBasedHeap
    :members:

TimeBasedSetHeap
----------------

A combination of `TimeBasedHeap` and `SetHeap`:

.. autoclass:: satella.coding.structures.TimeBasedSetHeap
    :members:

Mixins
======

Mixins are classes whose constructor you do not need to invoke. They magically
endow your class with chosen properties, often by overloading their specific
special methods.

ComparableAndHashableByInt
--------------------------

.. autoclass:: satella.coding.ComparableAndHashableByInt
    :members:

OmniHashableMixin
-----------------

If you need quick __hash__ and __eq__ operators from listed fields of the class.

.. autoclass:: satella.coding.structures.OmniHashableMixin
    :members:

ComparableAndHashableBy
-----------------------

.. autoclass:: satella.coding.structures.ComparableAndHashableBy
    :members:

StrEqHashableMixin
------------------

A class that outfits your class with __eq__ and __hash__ based off the str() value of the
class. So you got to define __str__ at the very least!

.. autoclass:: satella.coding.structures.StrEqHashableMixin
    :members:

ReprableMixin
-------------

If you need to provide a quick __repr__ for your classes:

.. autoclass:: satella.coding.structures.ReprableMixin
    :members:

HashableIntEnum
---------------

An enum.IntEnum that can be __hash__ed

.. autoclass:: satella.coding.structures.HashableIntEnum
    :members:


ComparableIntEnum
-----------------

An enum.IntEnum that you can compare by it's values

.. autoclass:: satella.coding.structures.ComparableIntEnum
    :members:

Immutable
---------

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


Singletons
==========

Singleton
---------

Makes the resulting object's ``__init__()`` be called at most once, then caches the object and returns the same
upon each instantiation.

.. autofunction:: satella.coding.structures.Singleton

SingletonWithRegardsTo
----------------------

Sometimes you just need an almost-singleton class, ie. class whose
instance will depend on first *n* arguments. This function makes it easy:

.. autofunction:: satella.coding.structures.SingletonWithRegardsTo

It will remember instances already created and return you a previously
created instance, keying on the first *n* arguments.

Dictionaries
============

ExclusiveWritebackCache
-----------------------

.. autoclass:: satella.coding.structures.ExclusiveWritebackCache

Use it as you would a normal dictionary.

DictObject
----------

DictObject is an object constructed out of a dict, that allows it's values to be obtained as getattr(), and not only
getitem().

.. autoclass:: satella.coding.structures.DictObject
    :members:

You can use the following function to recursively turn every dict into a DictObject

.. autofunction:: satella.coding.structures.apply_dict_object

frozendict
----------

A dictionary that can't be modified. I didn't import the one from _frozendict PyPI package,
because it failed on Python 3.9.
It is additionally hashable and __eq__-able

.. _frozendict: https://pypi.org/project/frozendict/

.. autoclass:: satella.coding.structures.frozendict

DictionaryView
--------------

.. autoclass:: satella.coding.structures.DictionaryView
    :members:


CacheDict
---------

.. autoclass:: satella.coding.structures.CacheDict
    :members:

SelfCleaningDefaultDict
-----------------------

.. autoclass:: satella.coding.structures.SelfCleaningDefaultDict
    :members:

ExpiringEntryDict
-----------------

.. autoclass:: satella.coding.structures.ExpiringEntryDict
    :members:


TwoWayDictionary
----------------

.. autoclass:: satella.coding.structures.TwoWayDictionary
    :members:


DirtyDict
---------

A dictionary that has also a flag called ``dirty`` that says
if it's been last modified since that flag was cleared.

The flag is initially (after the dict has been created)
set to False.

.. autoclass:: satella.coding.structures.DirtyDict
    :members:

KeyAwareDefaultDict
-------------------

.. autoclass:: satella.coding.structures.KeyAwareDefaultDict

Other structures
================

typednamedtuple
---------------

It's a named tuple, but it has typed fields. You will get a TypeError if you
try to assign something else there.

.. autofunction:: satella.coding.structures.typednamedtuple

HashableWrapper
---------------

.. autoclass:: satella.coding.structures.HashableWrapper

Ranking
-------

.. autoclass:: satella.coding.structures.Ranking
    :members:

SortedList
----------

.. autoclass:: satella.coding.structures.SortedList
    :members:

SliceableDeque
--------------

.. autoclass:: satella.coding.structures.SliceableDeque
    :members:

Proxy
-----

.. autoclass:: satella.coding.structures.Proxy
    :members:
