import logging
import os

import psutil

logger = logging.getLogger(__name__)


class LockIsHeld(Exception):
    """
    Lock is held by someone

    pid -- PID of the holder, who is alive
    """

    def __init__(self, pid):
        self.pid = pid


class PIDFileLock:
    """
    Acquire a PID lock file.

    Usable also on Windows

    Usage:

    >>> with PIDFileLock('myservice.pid'):
    >>>     ... rest of code ..

    Or alternatively

    >>> pid_lock = PIDFileLock('myservice.pid')
    >>> pid_lock.acquire()
    >>> ...
    >>> pid_lock.release()

    The constructor doesn't throw, __enter__ or acquire() does, one of:

   * LockIsHeld - lock is already held. This has two attributes - pid (int), the PID of holder,
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
            self.file_no = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except (OSError, FileExistsError):
            with open(self.path, 'r') as fin:
                data = fin.read().strip()

            try:
                pid = int(data)
            except ValueError:
                os.unlink(self.path)
                return self.acquire()

            if pid in {x.pid for x in psutil.process_iter()}:
                raise LockIsHeld(pid)
            else:
                # does not exist
                os.unlink(self.path)
                return self.acquire()

        fd = os.fdopen(self.file_no, 'w')
        fd.write(str(os.getpid()) + '\n')
        fd.close()

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
