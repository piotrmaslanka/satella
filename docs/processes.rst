=========
processes
=========

Note that this function will consume stdout as soon as it's
available, so that you don't need to worry about
the buffer overflowing and such.

.. autofunction:: satella.processes.call_and_return_stdout

This is a subprocess helper:

.. autofunction:: satella.processes.read_nowait
