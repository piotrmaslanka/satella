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

    def __init__(self, pid, is_alive):
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
            self.fileno = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except (FileExistsError, IOError, OSError):
            try:
                with open(self.path, 'r') as flock:
                    try:
                        data = flock.read().strip()
                        pid = int(data)
                    except ValueError:
                        if self.delete_on_dead:
                            try:
                                os.unlink(self.path)
                            except PermissionError:
                                raise FailedToAcquire('Cannot unlink the lock file')
                            else:
                                return self.acquire()
                        else:
                            raise FailedToAcquire(
                                'PID file found but doesn''t have an int (contains "%s") skipping' % (data,))
                    else:
                        # Is this process alive?
                        try:
                            os.kill(pid, 0)
                        except OSError:  # dead
                            if self.delete_on_dead:
                                os.unlink(self.path)
                                return self.acquire()  # retry acquisition
                            else:
                                raise LockIsHeld(pid, False)
                        else:
                            raise LockIsHeld(pid, True)
            except PermissionError as e:
                raise FailedToAcquire(repr(e))
        else:
            file = open(self.fileno)
            file.write(str(os.getpid()))
            file.flush()
            self.success = True

    def __enter__(self):
        self.acquire()


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
