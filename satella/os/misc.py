import os
import sys


def is_running_as_root() -> bool:
    """
    Is this process running as root?

    Checks whether EUID is 0

    :return: bool
    :raises OSError: called on Windows!
    """

    if sys.platform.startswith('win'):
        raise OSError('Routine unavailable on Windows!')

    return os.geteuid() == 0


def suicide(kill_entire_pg: bool = True) -> None:
    """
    Kill self.

    :param kill_entire_pg: whether to kill entire PG if a session leader
    :raises NotImplementedError: called on Windows!
    """

    if sys.platform.startswith('win'):
        raise NotImplementedError('suicide() not yet supported on Windows! (see issue #37)')

    mypid = os.getpid()
    kill = os.killpg if kill_entire_pg and os.getpgid(0) == mypid else os.kill
    kill(mypid, 9)