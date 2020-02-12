POSIX-specifics
===============

Note that in blatant disregard of this name's module some of these routines will work on Windows. So, a routine
is available on Windows unless stated otherwise.

suicide
-------

Kill your process (and your process group). Does not work on Windows (NotImplementedError). See issue #37 on GitHub.

.. autofunction:: satella.posix.suicide

daemonize
---------

Become a daemonized process. Does not work on Windows (OSError).

.. autofunction:: satella.posix.daemonize

hang_until_sig
--------------

Sleep until a signal is received.

.. autofunction:: satella.posix.hang_until_sig


is_running_as_root
------------------

Return if running as root. Routine unavailable on Windows (OSError).

.. autofunction:: satella.posix.is_running_as_root


PIDFileLock
--------------

This is meant to acquire a lock on a file.

.. autoclass:: satella.posix.PIDFileLock
    :members:

.. autoclass:: satella.exceptions.LockIsHeld
