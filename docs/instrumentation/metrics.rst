Metrics
-------

Metrics and instruments are a system to output real-time statistics.

Metrics are defined and meant to be used in a similar way
to Python logging.
It has a name (hierarchical, dot-separated),
that does not have to correspond to particular
modules or classes. It can be in one of 3 states:

* DISABLED
* RUNTIME
* DEBUG
* INHERIT

By default, it runs in *RUNTIME* mode. This means that statistics
are collected only from metrics of this
instrument that are set to at least RUNTIME. If a user wants to
dig deeper, it can switch the instrument to 
DEBUG, which will cause more data to be registered. If a metric 
is in state INHERIT, it will inherit the metric level from it's
parent, traversing the tree if required.

INHERIT is the default state for all other metrics than root,
for root the default is RUNTIME.

You can switch the metric anytime by assigning a correct value to
it's ``level`` property, or by specifying it's metric level during a call to ``getMetric()``.

Note that a decision to accept/reject a ``handle()``-provided value happens
when ``handle()`` is called, based on current level. If you change
the level, it may take some time for the metric to return correct
values.

The call to ``getMetric()`` is specified as follows

.. autofunction:: satella.instrumentation.metrics.getMetric

You obtain metrics using ``getMetric()`` as follows:

    ``metric = getMetric(__name__+'.StringMetric', 'string', RUNTIME, **kwargs)``

Where the second argument is a metric type. Following metric types
are available:

* base - for just a container metric
* int - for int values
* float - for float values
* counter - starts from zero, increments or decrements the counter value. Also optionally
  can register the amount of calls

.. autoclass:: satella.instrumentation.metrics.metric_types.CounterMetric

* cps - will count given amount of calls to handle() during last
  time period, as specified by user

    .. autoclass:: satella.instrumentation.metrics.metric_types.ClicksPerTimeUnitMetric

* quantile - a metric that counts a rolling window of values,
  and provides for a way to calculate percentiles

    .. autoclass:: satella.instrumentation.metrics.metric_types.QuantileMetric

Note that ``quantile.measure()`` will include time spent
processing the generator's content by the client, so you might
want to avoid measuring generators. However,
if this is the behaviour that you want, you get it.

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