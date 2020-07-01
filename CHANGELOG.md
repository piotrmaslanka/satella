# v2.8.13

* enabled calling `exception_handler` without specifying priority
* `call_and_return_stdout` will now raise `TimeoutError` if the task failed to complete
    within given timeout
