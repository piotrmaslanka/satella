sequences
=========

choose
------

To return the single element that returns true on given callable, use the following function:

.. autofunction:: satella.coding.sequences.choose

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
