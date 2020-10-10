# v2.11.26

* fix exception hierarchy in futures
* extended Traceback to fetch current stack frame if no exception is in progress and no stack frame is given
* added a feature to load a Traceback from a stream
* added __eq__ methods to Traceback classes
* fixed a bug with unserializing a Traceback from JSON
* `Traceback.from_pickle` will raise a `ValueError` if the pickled object is not a Traceback
* added `CountingDict`
* added get_instances_for_singleton and delete_singleton_for
* some minor corrections thanks to PyCharm
* deprecated `count(start_at=)`
* renamed the argument in `half_cartesian`
* minor typing, refactors and docs changes
