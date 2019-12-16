# v2.1.6

* added [json](satella/json.py) support

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
