POSIX-specifics
===============

suicide
-------

Kill your process (and your process group)

.. autofunction:: satella.posix.suicide

daemonize
---------

Become a daemonized process

.. autofunction:: satella.posix.daemonize


is_running_as_root
------------------

Return if running as root

.. autofunction:: satella.posix.is_running_as_root


AcquirePIDLock
--------------

This is meant to acquire a lock on a file.

.. autoclass:: satella.posix.AcquirePIDLock
    :members:

.. autoclass:: satella.posix.LockIsHeld
