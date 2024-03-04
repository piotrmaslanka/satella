CPU time
========

Satella's cpu_time helps your processes play nice with the overall CPU usage, ie. deferring
non-critical tasks to until CPU usage falls lower than the average.

You can even check how much CPU is your process using.

cpu_time does this by periodically monitoring CPU's usage and building your usage profile.
The profile is refreshed each X minutes.

.. warning:: Note that running the following procedures will launch a background daemonic thread
    spawning to gather data. This thread will run only once, and it will be daemonic, but it will use
    some of the CPU. If you don't call any of these, the thread won't be spawned.

.. autofunction:: satella.instrumentation.cpu_time.calculate_occupancy_factor

.. autofunction:: satella.instrumentation.cpu_time.sleep_cpu_aware


Here's the primary thread you can use to work with things:

.. autoclass:: satella.instrumentation.cpu_time.CPUTimeManager
    :members:

And here's a helpful variant of
:py:class:`satella.coding.concurrent.IntervalTerminableThread`:

.. autoclass:: satella.instrumentation.cpu_time.CPUTimeAwareIntervalTerminableThread
    :members:

.. autofunction:: satella.instrumentation.cpu_time.get_own_cpu_usage


.. autoclass:: satella.instrumentation.cpu_time.pCPUtimes
    :members:
