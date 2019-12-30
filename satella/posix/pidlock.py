import logging
import os

logger = logging.getLogger(__name__)


class LockIsHeld(Exception):
    """
    Lock is held by someone
    """


class AcquirePIDLock:
    """
    Acquire a PID lock file.

    Usage:

    >>> with AcquirePIDLock('myservice.pid'):
    >>>     ... rest of code ..

    Or alternatively

    >>> pid_lock = AcquirePIDLock('myservice.pid')
    >>> pid_lock.acquire()
    >>> ...
    >>> pid_lock.release()

    The constructor doesn't throw, __enter__ or acquire() does, one of:

    * AcquirePIDLock.FailedToAcquire - base class for errors. Thrown if can't read the file
    * AcquirePIDLock.LockIsHeld - lock is already held. This has two attributes - pid (int), the PID of holder,
                                  and is_alive (bool) - whether the holder is an alive process
    """

    def __init__(self, pid_file, base_dir=u'/var/run', delete_on_dead=False):
        """
        Initialize a PID lock file object

        :param pid_file: rest of path
        :param base_dir: base lock directory
        """
        self.delete_on_dead = delete_on_dead
        self.path = os.path.join(base_dir, pid_file)
        self.fileno = None

    def release(self):
        if self.fileno is not None:
            os.close(self.fileno)
            os.unlink(self.path)

    def acquire(self):
        """
        Acquire the PID lock

        :raises LockIsHeld: if lock if held
        :raises FailedToAcquire: if for example a directory exists in that place
        """
        try:
            self.fileno = os.open(self.path, os.O_CREAT | os.O_EXCL)
        except (FileExistsError, IOError, OSError):
            try:
                os.unlink(self.path)
            except OSError:
                raise LockIsHeld()
            else:
                return self.acquire()

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
