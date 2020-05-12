# v2.7.24

* `Proxy` objects will suceed isinstance check on the objects that they wrap
    * as a side effect both `Proxy` and `LockedDataset` are no longer Generic
* added `AtomicNumber`
* added `n_th`
* fixed `Multirun` not supporting empty arrays
