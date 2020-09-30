# v2.11.20

* unit testing engine changed from nose2 to pytest, since nose2 couldn't run tests on multiple threads
    It's much faster this way.
* added extra wait for the futures in `sync_threadpool`
* added `satella.dao`
