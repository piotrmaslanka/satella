import subprocess
import typing as tp

from .exceptions import ProcessFailed


def call_and_return_stdout(args: tp.Union[str, tp.List[str]],
                           expected_return_code: int = 0, **kwargs) -> tp.Union[bytes, str]:
    """
    Call a process and return it's stdout.

    :param args: arguments to run the program with. If passed a string, it will be split on space.
    :param expected_return_code: an expected return code of this process. 0 is the default. If process
        returns anything else, ProcessFailed will be raise
    :param ProcessFailed: process' result code was different from the requested
    """
    if isinstance(args, str):
        args = args.split(' ')

    kwargs['capture_output'] = True

    proc = subprocess.run(args, **kwargs)

    if proc.returncode != expected_return_code:
        raise ProcessFailed(proc.returncode)
    else:
        return proc.stdout


