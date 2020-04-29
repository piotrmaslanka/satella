import subprocess
import typing as tp
import threading
import logging

from .exceptions import ProcessFailed

logger = logging.getLogger(__name__)


def read_nowait(process: subprocess.Popen, output_list: tp.List[str]):
    try:
        while process.stdout.readable():
            line = process.stdout.readline()
            output_list.append(line)
    except (IOError, OSError):
        pass


def call_and_return_stdout(args: tp.Union[str, tp.List[str]],
                           timeout: tp.Optional[int] = None,
                           expected_return_code: int = 0, **kwargs) -> tp.Union[bytes, str]:
    """
    Call a process and return it's stdout.

    Everything in kwargs will be passed to subprocess.Popen

    :param args: arguments to run the program with. If passed a string, it will be split on space.
    :param timeout: amount of seconds to wait for the process result. If process does not complete
        within this time, it will be sent a SIGKILL
    :param expected_return_code: an expected return code of this process. 0 is the default. If process
        returns anything else, ProcessFailed will be raise
    :param ProcessFailed: process' result code was different from the requested
    """
    if isinstance(args, str):
        args = args.split(' ')
    logger.warning('Modifying kwargs')
    kwargs['stdout'] = subprocess.PIPE

    stdout_list = []

    logger.warning('Starting popen')
    proc = subprocess.Popen(args, **kwargs)
    reader_thread = threading.Thread(target=read_nowait, args=(proc, stdout_list), daemon=True)
    logger.warning('Starting rt')
    reader_thread.start()
    logger.warning('Waiting for termination')

    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
    logger.warning('Terminated')

    if proc.returncode != expected_return_code:
        raise ProcessFailed(proc.returncode)
    else:
        if kwargs.get('encoding', None) is None:
            return b''.join(stdout_list)
        else:
            return ''.join(stdout_list)


