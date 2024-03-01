============
OS-specifics
============

Note that satella's `posix` submodule is a deprecated alias for `os`

Note that in blatant disregard of this name's module some of these routines will work on Windows. So, a routine
is available on Windows unless stated otherwise.

whereis
-------

.. autofunction:: satella.os.whereis

suicide
-------

Kill your process (and your process group). Does not work on Windows (NotImplementedError). See issue #37 on GitHub.

.. autofunction:: satella.os.suicide

daemonize
---------

Become a daemonized process. Does not work on Windows (OSError).

.. autofunction:: satella.os.daemonize

hang_until_sig
--------------

Sleep until a signal is received.

.. autofunction:: satella.os.hang_until_sig


is_running_as_root
------------------

Return if running as root. Routine unavailable on Windows (OSError).

.. autofunction:: satella.os.is_running_as_root


PIDFileLock
--------------

This is meant to acquire a lock on a file.

.. autoclass:: satella.os.PIDFileLock
    :members:
