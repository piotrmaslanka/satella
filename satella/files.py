import logging
import typing as tp
import re
import os

logger = logging.getLogger(__name__)

__all__ = ['read_re_sub_and_write', 'find_files']


def read_re_sub_and_write(path: str, pattern: tp.Union[re.compile, str],
                          repl: tp.Union[tp.Callable[[None], str]]) -> None:
    """
    Read a text file, treat with re.sub and write the contents

    :param path: path of file to treat
    :param pattern: regexp compiled pattern or a string, a pattern to match the file contents
    :param repl: string or a callable(re.Match)->str to replace the contents
    """
    with open(path, 'r') as f_in:
        data = f_in.read()

    if isinstance(pattern, str):
        data = re.sub(pattern, repl, data)
    else:
        data = pattern.sub(repl, data)

    with open(path, 'w') as f_out:
        f_out.write(data)


def find_files(path: str, wildcard: str = r'(.*)') -> tp.Iterator[str]:
    """
    Look at given path's files and all subdirectories and return an iterator of
    file names (paths included) that conform to given wildcard.

    :param path: path to look into.
    :param wildcard: a regular expression to match
    :return: paths with the files. They will be relative paths, relative to path
    """
    for filename in os.listdir(path):
        if os.path.isdir(os.path.join(path, filename)):
            for file in find_files(os.path.join(path, filename), wildcard):
                yield os.path.join(filename, file)
        elif re.match(wildcard, filename):
            yield filename
