=======================
Sequences and iterators
=======================

Rolling averages
================

.. autoclass:: satella.coding.sequences.RollingArithmeticAverage
    :members:

Standard routines
=================

length
------

.. autofunction:: satella.coding.length

IteratorListAdapter
-------------------

.. autoclass:: satella.coding.sequences.IteratorListAdapter
    :members:

to_iterator
-----------

.. autofunction:: satella.coding.sequences.to_iterator

map_list
--------

.. autofunction:: satella.coding.sequences.map_list

unique
------

.. autofunction:: satella.coding.sequences.unique

iterate_callable
----------------

.. autofunction:: satella.coding.sequences.iterate_callable

choose
------

To return the first single element that returns true on given callable,
use the following function:

.. autofunction:: satella.coding.sequences.choose

choose_one
----------

Does the same thing as choose, but exhausts the generator and checks if there are no multiple
elements matching the callable. If there are, raises ValueError.

.. autofunction:: satella.coding.sequences.choose_one


AlreadySeen
-----------

.. autoclass:: satella.coding.sequences.AlreadySeen
    :members:


filter_out_nones
----------------

.. autofunction:: satella.coding.sequences.filter_out_nones


index_of
--------

.. autofunction:: satella.coding.sequences.index_of

index_of_max
------------

.. autofunction:: satella.coding.sequences.index_of_max

f_range
-------

.. autofunction:: satella.coding.sequences.f_range

filter_out_false
----------------

.. autofunction:: satella.coding.sequences.filter_out_false


try_close
---------

.. autofunction:: satella.coding.sequences.try_close


n_th
----

.. autofunction:: satella.coding.sequences.n_th


append_sequence
---------------

.. autofunction:: satella.coding.sequences.append_sequence

take_n
------

For the rare moments, when you wish you could just do:

::

    iterator: tp.Iterator[T] = iterator
    n_elements: tp.List[T] = iterator[:n]

But it doesn't let you do this, because iterator is not subscriptable.
However, this function comes to the rescue:

.. autofunction:: satella.coding.sequences.take_n


infinite_iterator
-----------------

.. autofunction:: satella.coding.sequences.infinite_iterator


is_instance
-----------

A factory for filter functions that check if given object is
an instance of something (or multiple classes, if passed a tuple
of classes). Use like that

::

    orders: tp.List[BaseOrder] = ...
    read_orders = filter(is_instance(ReadOrder), orders)

.. autofunction:: satella.coding.sequences.is_instance


is_last
-------

.. autofunction:: satella.coding.sequences.is_last


enumerate2
----------

.. autofunction:: satella.coding.sequences.enumerate2


smart_enumerate
---------

.. autofunction:: satella.coding.sequences.smart_enumerate


smart_zip
---------

.. autofunction:: satella.coding.sequences.smart_zip


add_next
--------

Sometimes you need to iterate through list and take also the next
element.

.. autofunction:: satella.coding.sequences.add_next


half_cartesian
--------------

Sometimes you need just a half of your Cartesian product, for example
for operations that are commutative (eg. checking for collisions,
if object A collides with B then B collides with A).

It helps you save time during computationally intensive operations.

This routine will return a iterator of tuple containing two elements
from the same set (ie. it will do something like a cartesian power of two).

.. autofuction:: satella.coding.sequences.half_cartesian


skip_first
----------

.. autofunction:: satella.coding.sequences.skip_first


zip_shifted
-----------

.. autofunction:: satella.coding.sequences.zip_shifted

This is deprecated. Use ``zip(shift(...))`` instead.


stop_after
----------

.. autofunction:: satella.coding.sequences.stop_after


group_quantity
--------------

.. autofunction:: satella.coding.sequences.group_quantity


iter_dict_of_list
-----------------

.. autofunction:: satella.coding.sequences.iter_dict_of_list


shift
-----

.. autofunction:: satella.coding.sequences.shift


other_sequence_no_longer_than
-----------------------------

.. autofunction:: satella.coding.sequences.other_sequence_no_longer_than


count
-----

.. autofunction:: satella.coding.sequences.count


length
------

.. autofunction:: satella.coding.sequences.length


Even and odd
------------

.. autofunction:: satella.coding.sequences.even

.. autofunction:: satella.coding.sequences.odd


Multirun
--------

.. autoclass:: satella.coding.sequences.Multirun

Generators
==========

.. autoclass:: satella.coding.sequences.ListWrapperIterator
    :members:

.. autoclass:: satella.coding.sequences.ConstruableIterator
    :members:

.. autofunction:: satella.coding.sequences.walk

.. autofunction:: satella.coding.chain

.. autofunction:: satella.coding.exhaust

.. autoclass:: satella.coding.hint_with_length
    :members:

Sometimes, you need the entire body of the generator to
run. It'd be a shame if someone decided to bail out on
you in the middle of the for loop. That's what
this class is for:

.. autoclass:: satella.coding.SelfClosingGenerator
    :members:

Using it on your generator objects will assure that they
will run to completion.

**Take care**: this won't work on PyPy due to it's nondeterministic
garbage collection!

Deleters
========

Objects that allow you to easily (and rather quickly)
remove elements from a list or a dict while iterating over
them with minimum memory overhead.

ListDeleter
-----------

.. autoclass:: satella.coding.ListDeleter
    :members:

DictDeleter
-----------

.. autoclass:: satella.coding.DictDeleter
    :members:
