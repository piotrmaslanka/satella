# v2.7.3

* _TBA_

# v2.7.3

* further extended `Caster`

# v2.7.2

* changed behaviour of MergingSource a bit
* added Caster to configuration schema

# v2.7.1

* API change reverted to before 2.7.0

# v2.7.0

*Possibly API breaking change: that's if you have
had the time to implement a feature which's been
out for like 4 hours*
* change in `DirtyDict`

# v2.6.4

* added `DirtyDict`

# v2.6.3

* added `satella.files.split`

# v2.6.1

* added `shift`
* added `other_sequence_no_longer_than`
* deprecated `zip_shifted`. Use `zip(shift(...))` instead

# v2.6.0

**Possibly API breaking change!**

You will be impacted if you assume that metric 
levels were ints. They are subclasses of an 
`enum.intEnum` how, but ints are still accepted
as a argument.

Furthermore, directly importing logging levels
(as RUNTIME, DEBUG, etc.) is deprecated. Import
MetricLevel instead.

These imports will be removed in v3.0.

* changed metric levels from ints to an enum

# v2.5.15

* added extra options to `log_exceptions`

# v2.5.14

* added `log_exceptions`

# v2.5.13

* `LockedStructure` is now generic
* added `returns` to `rethrow_as`
* patched `DictObject` to inherit from `UserDict` 
  instead of `dict`
* imports will log it's problem via warning, and now
  to the log anymore
* added [semantic versioning](https://semver.org/spec/v2.0.0.html) 

# v2.5.12

* added `iter_dict_of_list`

# v2.5.11

* removed redundant loggers
* added `LockedStructure`
* added `Proxy`

# v2.5.10

* exported CodedCustomExceptionMetaclass
* adde `group_quantity`

# v2.5.9

* added `MutableMapping` to `TwoWayDictionary`
* added `MutableSequence` to `SliceableDeque`
* added `CodedCustomException`

# v2.5.8

* added `pop` and `popleft` to SortedList

# v2.5.7

* optimized `Ranking`
* added `SlicableDeque`

# v2.5.6

* added `SortedList`

# v2.5.5

* added `TwoWayDictionary`
* added `Ranking`

# v2.5.4

* changed the behavior of `find_files`
* fixed a bug in `MemoryPressureManager` wherein consecutive states were
  not entered

# v2.5.3

* added extra options to `find_files`
* refactored `find_files`

# v2.5.2

* added `find_files`

# v2.5.1

* bugfix release: fixed constructor for `Not` in `MemoryPressureManager`

# v2.5.0

* added `CallableMetric`
* added `MemoryPressureManager`

# v2.4.45

* added capability for Configuration to execute arbitary Python

# v2.4.44

* added typing for some members
* added __slots__ to most classes
* added test for MemoryErrorHandler (at last!)

# v2.4.43

* added `HashableWrapper`
* made `CallableGroup` thread-safe 

# v2.4.42

* added `DictionaryView`
* fixed export all from `satella.coding.structures`
* added `__slots__` in multiple places

# v2.4.41

* added the context manager syntax for `Monitor`
  Please note that `Monitor.acquire()` syntax will not be deprecated, owing to 
  being a parallel to `Monitor.release()` which may be useful when we're
  already holding the lock from another source (eg. decorator)

# v2.4.40

* fixed problems with __copy__stemming from https://github.com/python/typing/issues/498
* docs fixed, Generics cleaned up

# v2.4.39

* added `Condition`

# v2.4.38

* `metric_data_collection_to_prometheus` won't export values marked as internal
* minor doc fixes
* added `MonitorList` and `MonitorDict`

# v2.4.37

* forbidden to instantiate `OmniHashableMixin` directly
* added `wrap_with`, `wrap_property`, `dont_wrap`

# v2.4.36

* bugfix release: more bulletproof `wraps`
* satella will internally use it's own `wraps` in lieu of `functools.wraps`

# v2.4.35

* added `Monitor.synchronize_on`

# v2.4.34

* added `wraps`

# v2.4.33

* added `stop_after`
* made zip_shifted use less memory when the shift is negative
  and argument is `Reversible`

# v2.4.32

* added `zip_shifted`

# v2.4.31

* added `skip_first`

# v2.4.30

* added `wrap_over` to `add_next`

# v2.4.29

* added `CustomException`
* added support for Futures in `measure()`

# v2.4.28

* added `half_product`

# v2.4.27

* added `attach_arguments`

# v2.4.26

* bugfix release: fixed `add_next` behaviour with regards to empty arguments

# v2.4.25

* bugfix release: fixed `add_next` behaviour with regards to empty arguments

# v2.4.24

* added `add_next`

# v2.4.23

* improved `is_last` to work on any iterable
* `internal` will be preserved during convering MetricData to JSON

# v2.4.22

* added `is_last`

# v2.4.21

* added default value for `staticvar`
* bugfix release: fixed linkfail metric

# v2.4.20

* deprecated `infinite_counter` (use `itertools.count` instead)
* added `is_instance` factory function

# v2.4.19

* added `internal` for `Metric`
* added `LinkfailMetric`

# v2.4.18

* added `measure.update()`
* added `measure.adjust()`
* starting time of `measure` is now defined
* added `import_class`
* added `take_n`

# v2.4.17

* changed the behaviour of `JSONEncoder` when it comes to serializing unknown objects
* moved the exception `LockIsHeld` to it's proper place
* fixed `dump_frames_on` not to log on **sys.stderr**
* added `satella.time.measure`

# v2.4.16

* can use `Metric.measure()` as a context manager
* added `measure()` to `FloatMetric` and `CounterMetric`
* added the `MetricAlreadyExists` exception

# v2.4.15

* fixed an import error that occurred on Python<3.7 when there were no requests installed
* bugfix release: commotion with `inf` in `HistogramMetric` fixed
* documented a behaviour in `precondition`
* added `has_keys`

# v2.4.14

* added `ge` in histograms
* fixed the warning in yaml loader

# v2.4.13

* fixed `precondition` to support kwargs
* added `short_none`

# v2.4.11

* added `HistogramMetric.measure()`

# v2.4.10

* renamed `HistogramMetric` to `SummaryMetric` to reflect that way things
  are done at [Prometheus](https://prometheus.io/docs/concepts/metric_types/#summary)
* added `HistogramMetric`

# v2.4.9

* bugfix release: fixed behaviour of `SimpleMetrics` with regards to labels

# v2.4.8

* added `infinite_counter`

# v2.4.7

* `satella.instrumentation.metrics` now exports `Metric`
* `QuantileMetric`(*quantile*) is now deprecated, use `HistogramMetric` (*histogram*) instead
* `TerminableThread.terminate(force=True)` will raise `NotImplementedError` on PyPy.

# v2.4.6

* added `satella.files`

# v2.4.5

* `JSONEncoder` will encode even non-JSON-able objects

# v2.4.4

* added `PrometheusHTTPExporterThread`
* added `EmptyMetric`

# v2.4.3

* better test coverage
* bugfix release - add_labels would modify the result's hash!

# v2.4.2

* bugfix release

# v2.4.1

* add `add_labels` for MetricData and MetricDataCollection

# v2.4.0

* major refactor for metrics
* added `frozendict`

# v2.3.16

* bugfix release, previous call would transform normal functions into generators and 
  we want to avoid that

# v2.3.15

* `QuantileMetric.measure` will properly measure generators now

# v2.3.14

* set default `enable_timestamp` to False

# v2.3.13

* a bugfix release - again

# v2.3.12

* a bugfix release - massive iterator lossage in `update`

# v2.3.11

* a bugfix release - update wouldn't

# v2.3.10

* a bugfix release - children naming

# v2.3.9

* added `CounterMetric`

# v2.3.8

* bugfix release: made it possible to use measure

# v2.3.7

* finally got Prometheus exporter right

# v2.3.6

* bugfix release - wrong annotation mechanics

# v2.3.5

* added capability to export metric timestamp
* added counting total amount of calls in `cps` metric

# v2.3.4

* bugfix in Prometheus exporter

# v2.3.3

* a bug fixed in `satella.instrumentation.metrics.json`
* added counting total amount of calls and total time
* removed `StringMetric`, as it is not readily Prometheus-exportable
* `PercentileMetric` renamed to `QuantileMetric`

# v2.3.2

* added aggregation to `PercentileMetric`

# v2.3.1

* more descriptive exceptions in descriptors

# v2.3.0

* significant refactor of [metrics](satella/instrumentation/metrics).

# v2.2.19

* doc fix in `OmniHashableMixin`

# v2.2.18

* added _SingletonWithRegardsTo_
* extra `functools.wraps()` on singleton's __init__

# v2.2.17

* added [choose](satella/coding/sequences/choose.py)

# v2.2.16

* `is_valid_schema` can be now passed in using kwargs

# v2.2.15

* added `DictObject.is_valid_schema`

# v2.2.14

* added `catch_exception`

# v2.2.13

* useless `print()`s removed in metrics
* additional unit tests and doc fixes
* added [SetHeap](satella/coding/structures/structures.py)

# v2.2.12

* bugfix where import_from would not pass all parameters to child calls
* removed debug logs from import_from
* far more extensive Python testing on Travis
* fixed exception auto-str
* DirectorySource has a new attribute *on_fail*
* switched to nose2 for tests

# v2.2.11

* bugfix and extra features added to *import_from*

# v2.2.10

* added [import_from](satella/imports.py)

# v2.2.9

* fixed `metaclass_maker`
* `self.assertEquals` -> `self.assertEqual` due to deprecation

# v2.2.8

* added [metaclass_maker](satella/coding/metaclasses.py)

# v2.2.7

* added inheritance from `abc` to Immutable

# v2.2.6

* added [Immutable](satella/coding/structures/immutable.py)

# v2.2.5

* made most of [satella.posix](satella/posix) routines behave
  themselves on Windows.
* bugfix in MemoryErrorHandler

# v2.2.4

* *bugfix release*: `signal.pause()` returned frequently, which translated
  to high CPU usage in [hang_until_sig](satella/posix/signals.py).

# v2.2.3

* renamed `AcquirePIDLock` to `PIDFileLock`
* more unit tests for `PIDFileLock`
    * it finally works

# v2.2.2

* more docs
* fixed `MemoryErrorExceptionHandler` not being importable from `satella.exception_handling`
* fixed the custom_hook for `MemoryErrorExceptionHandler`: it won't
  kill everything if the custom_hook returns True
* added an unit test for `precondition` 
* `Heap` now inherits from `UserList`

# v2.2.1

* added [TerminableThread](satella/coding/concurrent/thread.py)
* **COMPATIBILITY BREAKERS**
    * `Singleton` and family are meant to be imported from `satella.coding.structures`
    * `CallableGroup` is meant to be imported from `satella.coding.concurrent`

# v2.1.11

* bugfix release: __all__ in [coding](satella/coding/__init__.py) fixed
* more docs

# v2.1.10

* added [metrics](satella/instrumentation/metrics)
* [documentation](https://satella.readthedocs.io/en/develop/) improved

# v2.1.9

* bugfix release: fixed an occurrence where next calls to 
  [hang_until_sig](satella/posix/signals.py) would return immediately

# v2.1.8

* bugfix release: removed prints from LockedDataset

# v2.1.7

* bugfix release, don't use 2.1.6

# v2.1.6

* added [json](satella/json.py) support
* added `apply_dict_object`
* multiple bugfixes, thanks to finally listening to PyCharm's code inspection

# v2.1.5

* bugfix release: proper recovery of union from a dict thru `descriptor_from_dict`

# v2.1.4

* bugfix release: removed a print() from Descriptor

# v2.1.3

* bugfix in MergingSource
* argument rename in MemoryErrorExceptionHandler `killpg` -> `kill_pg`
* added the Union descriptor

# v2.1.2

* modified EnvironmentSource to accept custom config names
* added new descriptor type _Boolean_
* added _install_dump_frames_on_
* changed _descriptor_from_dict_ to assume optionality 
  when default value is provided
* dict descriptor will display the value if it's not a dict
* translated the [CHANGELOG](CHANGELOG.md) to English
* fixed (with an unit test) a bug wherein _EnvironmentSource_ raising an exception would fail

# v2.1.1

* removed support for Python 2.7
* most of the typecheck module was cut
* implemented tracking standard stack frames, not only the exception ones
* added support for _DictObject_
* added _exception_handling_ and _configuration_

## v2.0.24

* added [LockedDataset](/satella/coding/concurrent/locked_dataset.py)
* added [static_var](/satella/coding/fun_static.py)
* added [treat_result_with](/satella/coding/decorators.py)

## v2.0.22

* fixes #14

## v2.0.22rc3

* fixes #15
* fixes #20
* fixes #21

## v2.0.22rc2

* fixes #18

## v2.0.22rc1

* fixes #16

## v2.0.21

* fixed #10
* fixed #11

## v2.0.20

* requirements were fixed

## v2.0.19

* added `checked_coerce` and `for_argument`
* added `precondition`
* deprecated `checked_coerce` and `coerce`

## v2.0.16 = v2.0.17 == v2.0.18

* added `OmniHashableMixin`
* fixed checker's behaviour facing `typing.*` annotations

## v2.0.15

* fixed `rethrow_as`
* Travis will now deploy to PyPI, not me
* added `typednamedtuple`
* fixed the behaviour of `coerce`

## v2.0.14

* added `rethrow_as`

## v2.0.13

* Python 3.4 is back in the game
* Default time for _TimeBasedHeap_ 
* Traceback() called when not exceptions will result in ValueError

## v2.0.12

* minor improvements to TimeBasedHeap
* added `self` to @typed
* added `Number` type to @typed
* Satella korzysta z [Code Climate](https://codeclimate.com/github/piotrmaslanka/satella)

## v2.0.11

* Heap added

## v2.0.10

* bugfix release

## v2.0.9

* `satella.coding.merge_dicts` added
