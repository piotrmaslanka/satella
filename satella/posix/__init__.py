"""
POSIX things
"""

import os

from .daemon import daemonize
from .pidlock import PIDFileLock, LockIsHeld
from .signals import hang_until_sig

__all__ = [
    'daemonize',
    'PIDFileLock', 'LockIsHeld',
    'hang_until_sig',
    'is_running_as_root',
    'suicide'
]


def is_running_as_root() -> bool:
    """
    Is this process running as root?

    Checks whether EUID is 0

    :return: bool
    """
    return os.geteuid() == 0


def suicide(kill_entire_pg: bool = True) -> None:
    """
    Kill self.

    :param kill_entire_pg: whether to kill entire PG if a session leader
    """
    mypid = os.getpid()
    kill = os.killpg if kill_entire_pg and os.getpgid(0) == mypid else os.kill
    kill(mypid, 9)
