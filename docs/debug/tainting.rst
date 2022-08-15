Tainting
========

Some times you need to register a handle
for your thread to monitor whether some
values have been used or not. All interactions with this
variable will infect your source, so you need a way to find them
and elliminate them. Satella's tainting is at your disposal.

.. warning:: Tainting won't work correctly on earlier versions
    than Python 3.7 due to the fact that per-opcode tracing was
    added there.

.. autoclass:: satella.debug.TaintingEnvironment
    :members:

.. autofunction:: satella.debug.taint

.. autofunction:: satella.debug.access_tainted

There is a class that is a thin proxy at the objects that
you taint, namely:

.. autoclass:: satella.debug.TaintedObject

This works rather similar to :class:`satella.coding.structures.Proxy`.
