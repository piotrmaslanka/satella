CPU time
========

Satella's cpu_time helps your processes play nice with the overall CPU usage, ie. deferring
non-critical tasks to until CPU usage falls lower than the average.

cpu_time does this by periodically monitoring CPU's usage and building your usage profile.
The profile is refreshed each X minutes.

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
