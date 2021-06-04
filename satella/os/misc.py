import stat
import typing as tp
import os
import sys
import warnings

from satella.coding import silence_excs


def whereis(name: str) -> tp.Iterator[str]:
    """
    Looking in PATH return a sequence of executable files having provided name.

    Additionally, on Windows, it will use PATHEXT.

    .. note:: on Windows name is supposed to be without extension!

    :param name: name of the executable to search for
    :return: an iterator of absolute paths to given executable
    """
    if sys.platform.startswith('win'):
        paths_to_look_in = os.environ.get('PATH', '').split(';')
        name = name.upper()
        available_extensions = os.environ.get('PATHEXT', '.com;.bat;.exe').upper().split(';')
    else:
        paths_to_look_in = os.environ.get('PATH', '').split(':')
        available_extensions = '',

    for directory in paths_to_look_in:
        with silence_excs(FileNotFoundError):
            for file in os.listdir(directory):
                path = os.path.join(directory, file)
                if 'x' not in stat.filemode(os.stat(path).st_mode):
                    continue

                if sys.platform.startswith('win'):  # a POSIX-specific check
                    file = file.upper()  # paths are not case-sensitive on Windows

                for extension in available_extensions:
                    if file == '%s%s' % (name, extension):
                        yield path


def is_running_as_root() -> bool:
    """
    Is this process running as root?

    Checks whether effective UID is 0

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
