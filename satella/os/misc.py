import os
import sys
import warnings


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

    :param kill_entire_pg: whether to kill entire PG if a session leader. Won't work on Windows.
    """
    my_pid = os.getpid()
    if sys.platform.startswith('win'):
        if kill_entire_pg:
            warnings.warn('Windows does not support process leader groups', RuntimeWarning)
        os.kill(my_pid, -9)

    if kill_entire_pg and os.getpgid(0) == my_pid:
        os.killpg(my_pid, 9)
    else:
        os.kill(my_pid, 9)
