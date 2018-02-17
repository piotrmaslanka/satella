# coding=UTF-8
from __future__ import print_function, absolute_import, division

import logging
import os

logger = logging.getLogger(__name__)


class FailedToAcquire(Exception):
    """Failed to acquire the process lock file"""


class LockIsHeld(FailedToAcquire):
    """
    Lock is held by someone

    Has two attributes:
        pid - integer - PID of the holder
        is_alive - bool - whether the holder is an alive process
    """


class AcquirePIDLock(object):
    """
    Acquire a PID lock file.

    Usage:

        with AcquirePIDLock('myservice.pid'):

            .. rest of code ..

    Exiting the context manager deletes the file.

    The constructor doesn't throw, __enter__ does, one of:

    * AcquirePIDLock.FailedToAcquire - base class for errors. Thrown if can't read the file
    * AcquirePIDLock.LockIsHeld - lock is already held. This has two attributes - pid (int), the PID of holder,
                                  and is_alive (bool) - whether the holder is an alive process
    """

    def __init__(self, pid, is_alive):
        super(LockIsHeld, self).__init__()

        self.pid = pid
        self.is_alive = is_alive

    def __init__(self, pid_file, base_dir=u'/var/run', delete_on_dead=False):
        """
        Initialize a PID lock file object

        :param pid_file: rest of path
        :param base_dir: base lock directory
        :param delete_on_dead: delete the lock file if holder is dead, and retry
        """
        self.delete_on_dead = delete_on_dead

        self.path = os.path.join(base_dir, pid_file)

        self.fileno = None

    def _acquire(self):
        """The mechanical process of acquisition"""
        try:
            self.fileno = os.open(self.path, os.O_CREAT | os.O_EXCL)
        except (IOError, OSError):
            try:
                with open(self.path, 'rb') as flock:
                    try:
                        pid = int(flock.read())
                    except ValueError:
                        logger.warning(
                            'PID file found but doesn''t have an int, skipping')
                        return
            except IOError as e:
                raise FailedToAcquire()

            # Is this process alive?
            try:
                os.kill(pid, 0)
            except OSError:  # dead
                raise LockIsHeld(pid, False)
            else:
                raise LockIsHeld(pid, True)

    def __enter__(self):
        try:
            self._acquire()
        except LockIsHeld as e:
            if self.delete_on_dead and (not e.is_alive):
                os.unlink(self.path)
                self._acquire()
            else:
                raise

        self.success = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.fileno is not None:
            os.close(self.fileno)
            os.unlink(self.path)
