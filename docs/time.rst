====
Time
====

parse_time_string
-----------------

Parse a time string into amount of seconds

.. autofunction:: satella.time.parse_time_string


measure
-------
Sometimes you just need to measure how long does a routine call take.

.. autoclass:: satella.time.measure
    :members:

Note that you might specify other things to represent as time,
such as "get the amount of free memory" value.

time_as_int
-----------

Syntactic sugar for `int(time.time())`.

.. autofunction:: satella.time.time_as_int

time_ms
----------
Syntactic sugar for `int(time.time()*1000)`

.. autofunction:: satella.time.time_ms

time_us
----------
Syntactic sugar for `int(time.time()*1000000)`

.. autofunction:: satella.time.time_us

sleep
-----

.. autofunction:: satella.time.sleep

ExponentialBackoff
------------------

.. autoclass:: satella.time.ExponentialBackoff
    :members:
