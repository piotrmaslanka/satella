# v2.17.11

* **bugfix** exceptions in `TerminableThread` that have definde 
`terminate_on` won't be swallowed anymore.
* added support for `terminate_on` to `IntervalTerminableThread`
    and `CPUTimeAwareIntervalTerminableThread`
