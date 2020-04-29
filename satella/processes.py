import subprocess
import typing as tp
import threading
import logging

from .exceptions import ProcessFailed

logger = logging.getLogger(__name__)


def read_nowait(process: subprocess.Popen, output_list: tp.List[str]):
    try:
        while process.poll() is None:
            line = process.stdout.read(2048)
            if line == '':
                break
            output_list.append(line)
    except (IOError, OSError):
        pass


def call_and_return_stdout(args: tp.Union[str, tp.List[str]],
                           timeout: tp.Optional[int] = None,
                           encoding: tp.Optional[str] = None,
                           expected_return_code: tp.Optional[int] = None,
                           **kwargs) -> tp.Union[bytes, str]:
    """
    Call a process and return it's stdout.

    Everything in kwargs will be passed to subprocess.Popen

    A bytes object will be returned if encoding is not defined, else stdout will be decoded
    according to specified encoding.

    :param args: arguments to run the program with. If passed a string, it will be split on space.
    :param timeout: amount of seconds to wait for the process result. If process does not complete
        within this time, it will be sent a SIGKILL
    :param encoding: encoding with which to decode stdout. If none is passed, it will be returned as a bytes object
    :param expected_return_code: an expected return code of this process. 0 is the default. If process
        returns anything else, ProcessFailed will be raise. If left default (None) return code won't be checked
        at all
    :raises ProcessFailed: process' result code was different from the requested
    """
    if isinstance(args, str):
        args = args.split(' ')
    kwargs['stdout'] = subprocess.PIPE

    stdout_list = []

    proc = subprocess.Popen(args, **kwargs)
    reader_thread = threading.Thread(target=read_nowait, args=(proc, stdout_list), daemon=True)
    reader_thread.start()

    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
    reader_thread.join()

    if encoding is None:
        result = b''.join(stdout_list)
    else:
        result = ''.join((row.decode(encoding) for row in stdout_list))

    if expected_return_code is not None:
        if proc.returncode != expected_return_code:
            raise ProcessFailed(proc.returncode, result)

    return result

