Cassandra
=========

**This module is available only if you have cassandra-driver installed**

wrap_future
-----------

.. autofunction:: satella.cassandra.wrap_future

parallel_for
------------

If you have multiple async requests that would hit multiple nodes
and you would prefer to make use of `execute_async` and want to better
make use of them, here's the routine to help you out.

.. autofunction:: satella.cassandra.parallel_for

Note that if you specify an iterable instead of a string or a `cassandra.query.Statement`,
different query will be applied to those arguments, as stemming from their ordering.
