# v2.26.6

* _TBA_

# v2.26.5

* added `get_current_traceback` and fixed `RunActionAfterGeneratorCompletes` and `run_when_iterator_completes` default
  exception handling plus better docs

# v2.26.4

* `run_when_iterator_completes` and `RunActionAfterGeneratorCompletes` will now support exceptions

# v2.26.3

* added `run_when_iterator_completes`

# v2.26.2

* RunActionAfterGeneratorCompletes won't call it's on_done action if closed prematurely
* more complete support for generators in RunActionAfterGeneratorCompletes

# v2.26.1

* added run_when_generator_completes and RunActionAfterGeneratorCompletes

# v2.26.0

* **breaking change**: DictObject will no longer announce it's presence via __str__ and __repr__. It will just display
  it's dictionary.
* nested creation of DictObject's was optimized

# v2.25.9

* fixed the modules page in documentation
* added choose_with_index

# v2.25.7

* paths changed in pyproject.toml
* removed prints from unit tests

# v2.25.6

* deprecated rethrow_as
* fixed circular import
* fixed a subtle bug in _CPUProfileBuilderThread.get_own_cpu_usage

# v2.25.5

* slight optimization for Heap.push_many
* bugfix for Heap.push and a deprecation
* changed how CallableGroup works - now every add adds a CancellableCallback
  and it's always true that CallableGroup has it's own cancellable callbacks.

# v2.25.4

* add JSONAbleDataObject
* improved typing for reraise_as
* added weak_refs to SingletonWithRegardsTo
* added jump_to_directory
* fixed get_size() to RuntimeError on PyPy instead of hanging
