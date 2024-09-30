# v2.25.8

* fixed the modules page

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
