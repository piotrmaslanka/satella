sequences
=========

choose
------

To return the single element that returns true on given callable, use the following function:

.. autofunction:: satella.coding.sequences.choose

n_th
----

.. autofunction:: satella.coding.sequences.n_th

take_n
------

For the rare moments, when you wish you could just do:

::

    iterator: tp.Iterator[T] = iterator
    n_elements: tp.List[T] = iterator[:n]

But it doesn't let you do this, because iterator is not subscriptable.
However, this function comes to the rescue:

.. autofunction:: satella.coding.sequences.take_n

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

Even and odd
------------

.. autofunction:: satella.coding.sequences.even

.. autofunction:: satella.coding.sequences.odd

Multirun
--------

.. autoclass:: satella.coding.sequences.Multirun
