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
        self.file_no = None

    def release(self):
        """
        Free the lock
        """
        if self.file_no is not None:
            os.unlink(self.path)
            self.file_no = None

    def acquire(self):
        """
        Acquire the PID lock

        :raises LockIsHeld: if lock if held
        """
        try:
            self.file_no = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        except (OSError, FileExistsError):
            with open(self.path, 'r') as fin:
                data = fin.read().strip()

            try:
                pid = int(data)
            except ValueError:
                os.unlink(self.path)
                return self.acquire()

            try:
                os.kill(pid, 0)
            except OSError:
                # does not exist
                os.unlink(self.path)
                return self.acquire()
            else:
                raise LockIsHeld()

        open(self.file_no).write(str(os.getpid()))
        os.close(self.file_no)

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
