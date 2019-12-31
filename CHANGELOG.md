# v2.2.4

* _TBA_

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
