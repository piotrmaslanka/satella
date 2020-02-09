import logging
import typing as tp
import re

logger = logging.getLogger(__name__)

__all__ = ['read_re_sub_and_write']


def read_re_sub_and_write(path: str, pattern: tp.Union[re.Pattern, str],
                          repl: tp.Union[tp.Callable[[re.Match], str]]) -> None:
    """
    Read a text file, treat with re.sub and write the contents

    :param path: path of file to treat
    :param pattern: re.Pattern or a string, a pattern to match the file contents
    :param repl: string or a callable(str)->str to replace the contents
    """
    with open(path, 'r') as f_in:
        data = f_in.read()

    if isinstance(pattern, re.Pattern):
        data = pattern.sub(repl, data)
    else:
        data = re.sub(pattern, repl, data)

    with open(path, 'w') as f_out:
        f_out.write(data)

