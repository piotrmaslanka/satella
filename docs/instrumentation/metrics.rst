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

By default, it runs in _runtime_ mode. This means that statistics
are collected only from metrics of this
instrument that are set to at least RUNTIME. If a user wants to
dig deeper, it can switch the instrument to 
DEBUG, which will cause more data to be registered. If a metric 
is in state INHERIT, it will inherit the metric level from it's
parent, traversing the tree if required.

You can switch the metric anytime by calling it's ``switch_level``
method, or by specifying it's metric level during a call to ``getMetric()``.

The call to ``getMetric()`` is specified as follows

.. autofunction:: satella.instrumentation.metrics.getMetric

You obtain metrics using ``getMetric()`` as follows:

    ``metric = getMetric(__name__+'.StringMetric', 'string', RUNTIME, **kwargs)``

Where the second argument is a metric type. Following metric types
are available:

* base - for just a container metric
* string - for string values
* int - for int values
* float - for float values
* cps - will count given amount of calls to handle() during last
  time period, as specified by user

    .. autoclass:: satella.instrumentation.metrics.metric_types.ClicksPerTimeUnitMetric

* percentile - a metric that counts a rolling window of values,
  and provides for a way to calculate percentiles

    .. autoclass:: satella.instrumentation.metrics.metric_types.PercentileMetric

Third parameter is optional. If set, all child metrics created 
during this metric's instantiation will receive such metric level.
If the metric already exists, it's level will be set to provided
metric level, if passed.

All child metrics (going from the root metric to 0) will be initialized
with the value that you just passed. In order to keep them in order,
an additional parameter passed to ``getMetric()``, ``metric_level``, if
specified, will set given level upon returning the even existing
metric.

If you don't specify it, the metric level for root metric will be
set to RUNTIME. Same if you specify INHERIT.

Note that a decision to accept/reject a ``handle()``-provided value happens
when ``handle()`` is called, based on current level. If you change
the level, it may take some time for the metric to return correct
values.

If you specify any kwargs, they will be delivered to the last
metric's in chain constructor.

Since metrics in Satella are primarily though out to end up
on a Prometheus, it is very important to understand
Prometheus' data model_.

.. _model: https://prometheus.io/docs/concepts/data_model/

Root metric's ``to_json`` will output a tree based hierarchy,
where keys are supposed to be concatenated with an underscore.
The last object in the dictionary is the leaf node.

The leaf node consists of a key `_` which maps the value,
and remaining keys being labels, and their respective values
being values.

The direct parent of a leaf may be a list. This aggregates
the labels and their values. These are generated only
by `LeafMetrics`.

.. autoclass:: satella.instrumentation.metrics.metric_types.LeafMetric
    :members:

On most metrics you can specify additional labels. They will serve
to create an independent "sub-metric" of sorts, eg.

::

    metric = getMetric('root', 'int')
    metric.runtime(2, label='value')
    metric.runtime(3, label='key')
    assert metric.to_json() == [{'label': 'value', '_': 2}, {'label': 'key', '_': 3}]

This functionality is provided by the below class:

.. autoclass:: satella.instrumentation.metrics.metric_types.base.EmbeddedSubmetrics
    :members:

Modifying returned JSON
=======================

JSON returned by the root metric's ``to_json()`` can be further modified:

If you need to insert some labels at every leaf node, use the following function:

.. autofunction:: satella.instrumentation.metrics.json.annotate_every_leaf_node_with_labels

If you need to merge two JSONs returned by metrics (eg. for a
metric exporter service) you can use the following function:

.. autofunction:: satella.instrumentation.metrics.json.update


Exporting data
==============

In order to export data to Prometheus, you can use the following function:

.. autofunction:: satella.instrumentation.metrics.exporters.json_to_prometheus

For example in such a way:

::

    def export_to_prometheus():
        metric = getMetric()
        return json_to_prometheus(metric.to_json())
