import subprocess
import threading
import typing as tp

from satella.coding.recast_exceptions import silence_excs

from .exceptions import ProcessFailed

__all__ = ['call_and_return_stdout']


@silence_excs((IOError, OSError))
def _read_nowait(process: subprocess.Popen, output_list: tp.List[str]) -> None:
    """
    To be launched as a daemon thread. This reads stdout and appends it's entries to a list.
    This should finish as soon as the process exits or closes it's stdout.
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
                           timeout: tp.Optional[int] = None,
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
        within this time, it will be sent a SIGKILL
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
    reader_thread = threading.Thread(name='stdout reader',
                                     target=_read_nowait,
                                     args=(proc, stdout_list),
                                     daemon=True)
    reader_thread.start()

    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        raise TimeoutError('Process did not complete within %s seconds' % (timeout, ))
    finally:
        reader_thread.join()

    if encoding is None:
        result = b''.join(stdout_list)
    else:
        result = ''.join((row.decode(encoding) for row in stdout_list))

    if expected_return_code is not None:
        if proc.returncode != expected_return_code:
            raise ProcessFailed(proc.returncode, result)

    return result
