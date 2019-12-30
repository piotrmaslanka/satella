import logging
import os

logger = logging.getLogger(__name__)


class LockIsHeld(Exception):
    """
    Lock is held by someone
    """


class FileLock:
    """
    Acquire a PID lock file.

    Usable also on Windows

    Usage:

    >>> with FileLock('myservice.pid'):
    >>>     ... rest of code ..

    Or alternatively

    >>> pid_lock = FileLock('myservice.pid')
    >>> pid_lock.acquire()
    >>> ...
    >>> pid_lock.release()

    The constructor doesn't throw, __enter__ or acquire() does, one of:

    * AcquirePIDLock.FailedToAcquire - base class for errors. Thrown if can't read the file
    * AcquirePIDLock.LockIsHeld - lock is already held. This has two attributes - pid (int), the PID of holder,
                                  and is_alive (bool) - whether the holder is an alive process
    """

    def __init__(self, pid_file, base_dir=u'/var/run'):
        """
        Initialize a PID lock file object

        :param pid_file: rest of path
        :param base_dir: base lock directory
        """
        self.path = os.path.join(base_dir, pid_file)
        self.fileno = None

    def release(self):
        """
        Free the lock
        """
        if self.fileno is not None:
            os.close(self.fileno)
            os.unlink(self.path)

    def acquire(self):
        """
        Acquire the PID lock

        :raises LockIsHeld: if lock if held
        """
        try:
            self.fileno = os.open(self.path, os.O_CREAT | os.O_EXCL)
        except (OSError, FileExistsError) as e:
            try:
                os.unlink(self.path)
            except Exception as e:
                import sys
                sys.stderr.write(str(type(e)) + '\n')
                raise LockIsHeld()
            else:
                return self.acquire()

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
