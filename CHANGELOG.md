# v.25.a7

* fixed circular import
* added __len__ to PeekableQueue
* fixed CallableGroup, added new class

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
