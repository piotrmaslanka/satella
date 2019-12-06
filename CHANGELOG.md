# v2.1

* removed support for Python 2.7
* most of the typecheck module was cut
* implemented tracking standard stack frames, not only the exception ones

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

* Naprawiono requirements

## v2.0.19

* Dodano `checked_coerce` i `for_argument`
* Dodano `precondition`
* Zdeprekowano `checked_coerce` i `coerce`

## v2.0.16 = v2.0.17 == v2.0.18

* Dodano `OmniHashableMixin`
* Poprawiono zachowanie type checkera w obliczu anotacji z `typing.*`

## v2.0.15

* Usprawnienia do `rethrow_as`
* Travis teraz wrzuca na PyPI, a nie ja :)
* Dodano `typednamedtuple`
* Poprawione zachowanie `coerce`

## v2.0.14

* Dodano `rethrow_as`

## v2.0.13

* Python 3.4 znów wspierany
* Domyślny czas dla TimeBasedHeap 
* Traceback uruchamiany bez wyjątku będzie rzucał ValueError

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
