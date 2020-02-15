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
