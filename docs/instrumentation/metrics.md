Metrics and instruments are a system to output real-time statistics.

_An instrument_ is a collection of metrics. It has a name (hierarchical, dot-separated),
that does not have to correspond to particular modules or classes. It can be in one of 3 states:

* Disabled
* Runtime
* Debug

By default, it runs in _runtime_ mode. This means that statistics are collected only from metrics of this
instrument that are set to at least RUNTIME. If a user wants to dig deeper, it can switch the instrument to 
DEBUG, which will cause more data to be registered.