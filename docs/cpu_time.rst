========
CPU time
========

Satella's cpu_time helps your processes play nice with the overall CPU usage, ie. deferring
non-critical tasks to until CPU usage falls lower than the average.

cpu_time does this by periodically monitoring CPU's usage and building your usage profile.
The profile is refreshed each X minutes.

.. autofunction:: satella.cpu_time.calculate_occupancy_factor

.. autofunction:: satella.cpu_time.sleep_except


