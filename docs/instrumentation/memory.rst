Memory pressure
===============

When faced with the risk of running low on memory, you know that some of your
programs' variables are cache. They can be discarded, dropped on the floor, to
be recomputed later.

Problem is, that they need a trigger to do it. Memory pressure management
from Satella solves that problem.

.. autofunction:: satella.instrumentation.memory.get_size

.. warning:: Using these conditions will spawn a daemon thread to monitor the memory usage
    in the background.

Defining severity levels
------------------------

To define a severity level, use the following classes:

.. autoclass:: satella.instrumentation.memory.GlobalAbsoluteValue

.. autoclass:: satella.instrumentation.memory.GlobalRelativeValue

.. autoclass:: satella.instrumentation.memory.LocalAbsoluteValue

.. autoclass:: satella.instrumentation.memory.LocalRelativeValue

Here you can either provide a callable or override the ``can_fire`` method

.. autoclass:: satella.instrumentation.memory.CustomCondition
    :members:

You can combine them with following operators:

.. autoclass:: satella.instrumentation.memory.All

.. autoclass:: satella.instrumentation.memory.Any

.. autoclass:: satella.instrumentation.memory.Not

Then, you make a list out of them. This list, with indices counted from 1,
signals what condition needs to be true for the program to enter given severity level.

Handlers
--------

It is impossible to go from severity level 1 to say 3 without hitting 2. 2 will
be hit by the way, the manager will call any handlers that are in the way.
Note that severity levels are concurrent - for example,
level 1 coexists with level 2, and if level 2 is in effect, that means
that level 1 is still in effect. You can register your handlers here:

.. autoclass:: satella.instrumentation.memory.MemoryPressureManager
    :members:

install_force_gc_collect
------------------------

If you want, you can install a GC handler that will
force a complete GC collection upon entering given severity level.

.. autofunction:: satella.instrumentation.memory.install_force_gc_collect

Dumping memory information
--------------------------

.. autofunction:: satella.instrumentation.memory.dump_memory_on

.. autofunction:: satella.instrumentation.memory.install_dump_memory_on
