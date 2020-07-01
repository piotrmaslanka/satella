# v2.8.13

* enabled calling `exception_handler` without specifying priority
* `call_and_return_stdout` will now raise `TimeoutError` if the task failed to complete
    within given timeout
* added power support to `AtomicNumber`
* slight refactor in `AtomicNumber`
* removed `end_on_keyboard_interrupt` from `hang_until_sig`
* unit test for `hang_until_sig` at last
