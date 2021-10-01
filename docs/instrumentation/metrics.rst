=======
Metrics
=======

Satella's metrics
=================

Metrics and instruments are a system to output real-time statistics.

Metrics are defined and meant to be used in a similar way
to Python logging.
It has a name (hierarchical, dot-separated),
that does not have to correspond to particular
modules or classes. It can be in one of 4 states:

* DISABLED
* RUNTIME
* DEBUG
* INHERIT

These are contained in a enum:

.. autoclass:: satella.instrumentation.metrics.MetricLevel

By default, it runs in *RUNTIME* mode. This means that statistics
are collected only from metrics of this
instrument that are set to at least RUNTIME. If a user wants to
dig deeper, it can switch the instrument to
DEBUG, which will cause more data to be registered. If a metric
is in state INHERIT, it will inherit the metric level from it's
parent, traversing the tree if required. The tree node separator is a dot in the
metric's name, eg. `satella.metrics.my_metric`.

INHERIT is the default state for all other metrics than root,
for root the default is RUNTIME. Root metric cannot be set to INHERIT,
as it would not make sense.

Also, if parent is RUNTIME and child is DEBUG, the metrics reported by the child won't be included
in parent metric data.

You can switch the metric anytime by assigning a correct value to
it's ``level`` property, or by specifying it's metric level during a call to ``getMetric()``.

Note that a decision to accept/reject a ``handle()``-provided value happens
when ``handle()`` is called, based on current level. If you change
the level, it may take some time for the metric to return correct
values.

The call to ``getMetric()`` is specified as follows

.. autofunction:: satella.instrumentation.metrics.getMetric

You obtain metrics using ``getMetric()`` as follows:

    ``metric = getMetric(__name__+'.StringMetric', 'string', MetricLevel.RUNTIME, **kwargs)``

Please note that metric name must match the following regex:

`[a-zA-Z_:][a-zA-Z0-9_:]*`

**internal** is for those cases where the application is the consumer of
the metrics, and you don't want them exposed to outside.
Take care to examine this field of ``MetricData`` if you
write custom exporters!

Where the second argument is a metric type. Following metric types
are available:

* base - for just a container metric
* int - for int values
* float - for float values

    .. autoclass:: satella.instrumentation.metrics.metric_Types.FloatMetric
        :members:

* empty - disregard all provided values, outputs nothing
* counter - starts from zero, increments or decrements the counter value. Also optionally
  can register the amount of calls

    .. autoclass:: satella.instrumentation.metrics.metric_types.CounterMetric
        :members:
* cps - will count given amount of calls to handle() during last
  time period, as specified by user

    .. autoclass:: satella.instrumentation.metrics.metric_types.ClicksPerTimeUnitMetric
        :members:

.. note:: Normally you should use a counter and calculate a rate() from it, but since some
          platforms suck at rate a decision was made to keep this.

* linkfail - for tracking whether given link is online or offline

    .. autoclass:: satella.instrumentation.metrics.metric_types.LinkfailMetric
        :members:

* summary - a metric that counts a rolling window of values,
  and provides for a way to calculate percentiles. Corresponds
  to Prometheus' summary_ metrics.

    .. autoclass:: satella.instrumentation.metrics.metric_types.SummaryMetric
        :members:

* histogram - a metric that puts given values into predefined buckets.
  Corresponds to Prometheus' histogram_ metric

    .. autoclass:: satella.instrumentation.metrics.metric_types.HistogramMetric
        :members:

* callable - a metric whose value is a result of a given callable

    .. autoclass:: satella.instrumentation.metrics.metric_types.CallableMetric
        :members:

* uptime - a metric to report uptime

    .. autoclass:: satella.instrumentation.metrics.metric_types.UptimeMetric
        :members:

.. _summary: https://prometheus.io/docs/concepts/metric_types/#summary
.. _histogram: https://prometheus.io/docs/concepts/metric_types/#histogram

Note that ``metric.measure()`` will include time spent
processing the generator's content by the client, so you might
want to avoid measuring generators. However,
if this is the behaviour that you want, you get it.

Note that if you request a different type of existing metric via `getMetric`,
an MetricAlreadyExists exception will be raised:

.. autoclass:: satella.exceptions.MetricAlreadyExists

Third parameter is optional. If set, all child metrics created
during this metric's instantiation will receive such metric level.
If the metric already exists, it's level will be set to provided
metric level, if passed.

All child metrics (going from the root metric to 0) will be initialized
with the value that you just passed. In order to keep them in order,
an additional parameter passed to ``getMetric()``, ``metric_level``, if
specified, will set given level upon returning the even existing
metric.

This will be set on all children **created by this call**. If you
have any children from previous calls, they will remain
unaffected.

If you specify any kwargs, they will be delivered to the last
metric's in chain constructor.

Since metrics in Satella are primarily though out to end up
on a Prometheus, it is very important to understand
Prometheus' data model_.

.. _model: https://prometheus.io/docs/concepts/data_model/

Root metric's ``to_metric_data`` will output a flat set, called
MetricDataCollection:

.. autoclass:: satella.instrumentation.metrics.MetricDataCollection
    :members:

which consists of MetricData:

.. autoclass:: satella.instrumentation.metrics.MetricData
    :members:

On most metrics you can specify additional labels. They will serve
to create an independent "sub-metric" of sorts, eg.

::

    metric = getMetric('root', 'int')
    metric.runtime(2, label='value')
    metric.runtime(3, label='key')
    assert metric.to_metric_data() == MetricDataCollection(MetricData('root', 2, {'label': value}),
                                                           MetricData('root', 3, {'label': 'key}))

This functionality is provided by the below class:

.. autoclass:: satella.instrumentation.metrics.metric_types.EmbeddedSubmetrics
    :members:

Rolling your own metrics
========================

In order to roll your own metrics, you must first subclass Metric.
You can subclass one of the following classes, to the best of your liking.
Please also refer to existing metric implementations on how to best subclass them.


.. autoclass:: satella.instrumentation.metrics.metric_types.Metric
    :members:


.. autoclass:: satella.instrumentation.metrics.metric_types.LeafMetric
    :members:


.. autoclass:: satella.instrumentation.metrics.metric_types.base.EmbeddedSubmetrics
    :members:

Remember to define a class attribute of CLASS_NAME, which is a string
defining how to call your metric. After everything is done, register it
by using the following decorator on your metric class

.. autofunction:: satella.instrumentation.metrics.metric_types.register_metric

To zip together two or more metrics, you can use the following class:

.. autoclass:: satella.instrumentation.metrics.AggregateMetric
    :members:

To automatically apply labels you can use this class:

.. autoclass:: satella.instrumentation.metrics.LabeledMetric
    :members:


Exporting data
==============

In order to export data to Prometheus, you can use the following function:

.. autofunction:: satella.instrumentation.metrics.exporters.metric_data_collection_to_prometheus

For example in such a way:

::

    def export_to_prometheus():
        metric = getMetric()
        return metric_data_collection_to_prometheus(metric.to_metric_data())

Dots in metric names will be replaced with underscores.

Or, if you need a HTTP server that will export metrics for Prometheus, use this class
that is a daemonic thread you can use to easily expose metrics to Prometheus:

.. autoclass:: satella.instrumentation.metrics.exporters.PrometheusHTTPExporterThread
    :members:

Useful data structures
======================

Sometimes you want to have some data structures with metrics about themselves.
Here go they:

.. autoclass:: satella.instrumentation.metrics.structures.MetrifiedThreadPoolExecutor
    :members:

.. autoclass:: satella.instrumentation.metrics.structures.MetrifiedCacheDict

.. autoclass:: satella.instrumentation.metrics.structures.MetrifiedLRUCacheDict

.. autoclass:: satella.instrumentation.metrics.structures.MetrifiedExclusiveWritebackCache

