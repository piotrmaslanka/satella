import subprocess
import typing as tp

from satella.coding.recast_exceptions import silence_excs
from .coding.concurrent import call_in_separate_thread
from .exceptions import ProcessFailed

__all__ = ['call_and_return_stdout', 'read_nowait']

from .time import parse_time_string


@call_in_separate_thread(daemon=True)
@silence_excs((IOError, OSError))
def read_nowait(process: subprocess.Popen, output_list: tp.List[str]):
    """
    This spawns a thread to read given process' stdout and append it to a list, in
    order to prevent buffer filling up completely.

    To retrieve entire stdout after process finishes do

    >>> ''.join(list)

    This thread will terminate automatically after the process closes it's stdout or finishes.
    """
    while True:
        with silence_excs(subprocess.TimeoutExpired):
            process.wait(timeout=0.1)
            line = process.stdout.read(2048)
            if line:
                output_list.append(line)
            else:
                break


def call_and_return_stdout(args: tp.Union[str, tp.List[str]],
                           timeout: tp.Optional[tp.Union[str, int]] = None,
                           encoding: tp.Optional[str] = None,
                           expected_return_code: tp.Optional[int] = None,
                           **kwargs) -> tp.Union[bytes, str]:
    """
    Call a process and return it's stdout.

    Everything in kwargs will be passed to subprocess.Popen

    A bytes object will be returned if encoding is not defined, else stdout will be decoded
    according to specified encoding.

    :param args: arguments to run the program with. Can be either a string or a list of strings.
    :param timeout: amount of seconds to wait for the process result. If process does not complete
        within this time, it will be sent a SIGKILL. Can be also a time string. If left at default,
        ie. None, timeout won't be considered at all.
    :param encoding: encoding with which to decode stdout. If none is passed, it will be returned as
        a bytes object
    :param expected_return_code: an expected return code of this process. 0 is the default. If
        process returns anything else, ProcessFailed will be raise. If left default (None) return
        code won't be checked at all
    :raises ProcessFailed: process' result code was different from the requested
    :raises TimeoutError: timeout was specified and the process didn't complete
    """
    kwargs['stdout'] = subprocess.PIPE

    stdout_list = []

    proc = subprocess.Popen(args, **kwargs)
    fut = read_nowait(proc, stdout_list)

    if timeout is not None:
        timeout = parse_time_string(timeout)

    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        raise TimeoutError('Process did not complete within %s seconds' % (timeout,))
    finally:
        fut.result()

    if encoding is None:
        result = b''.join(stdout_list)
    else:
        result = ''.join((row.decode(encoding) for row in stdout_list))

    if expected_return_code is not None:
        if proc.returncode != expected_return_code:
            raise ProcessFailed(proc.returncode, result)

    return result
