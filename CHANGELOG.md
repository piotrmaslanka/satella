# v2.14.24

* `measure.time_remaining` will not return negative values
* `MemoryErrorExceptionHandler` will use less memory procesing `MemoryError`s
* `merge_series` will now throw a `ValueError` instead of `RuntimeError`
* add `MemoryPressureManager.register_on_memory_normal`
* fixed a bug where `CallableGroup` would not remove it's one-shot callbacks
    * this fixed a bug with `MemoryPressureManager` entering a state too often
