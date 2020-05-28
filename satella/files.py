import typing as tp
import re
import os
import codecs

__all__ = ['read_re_sub_and_write', 'find_files', 'split', 'read_in_file', 'write_to_file']

SEPARATORS = {'\\', '/'}
SEPARATORS.add(os.path.sep)


def _has_separator(path: str) -> bool:
    # handle Windows case
    if len(path) == 3:
        if path.endswith(':/') or path.endswith(':\\'):
            return False
    return any(map(lambda x: x in path, SEPARATORS))


def split(path: str) -> tp.List[str]:
    """
    An exact reverse of os.path.join

    Is is true that

    >>> os.path.join(split(a)) == a
    """
    data = list(os.path.split(path))
    while _has_separator(data[0]):
        data = list(os.path.split(data[0])) + data[1:]
    return data


def write_to_file(path: str, data: tp.Union[bytes, str], encoding: tp.Optional[str] = None) -> None:
    """
    Write provided content as a file, applying given encoding (or data is bytes, if none given)

    :param path: Path to put the file under
    :param data: Data to write. Must be bytes if no encoding is given, str otherwise
    :param encoding: Encoding. Default is None, which means no encoding (bytes will be written)
    """
    if encoding is None:
        file = open(path, 'wb')
    else:
        file = codecs.open(path, 'wb', encoding)

    try:
        file.write(data)
    finally:
        file.close()


def read_in_file(path: str, encoding: tp.Optional[str] = None) -> tp.Union[bytes, str]:
    """
    Opens a file for reading, reads it in, converts to given encoding (or returns as bytes if not given),
    and closes it.
    """
    if encoding is None:
        file = open(path, 'rb')
    else:
        file = codecs.open(path, 'rb', encoding)

    try:
        return file.read()
    finally:
        file.close()


def read_re_sub_and_write(path: str, pattern: tp.Union[re.compile, str],
                          repl: tp.Union[tp.Callable[[tp.Any], str]]) -> None:
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


def _cond_join(prefix: tp.Optional[str], filename: str) -> str:
    """or a conditional os.path.join"""
    if prefix is None:
        return filename
    else:
        return os.path.join(prefix, filename)


def find_files(path: str, wildcard: str = r'(.*)',
               prefix_with: tp.Optional[str] = None,
               scan_subdirectories: bool = True,
               apply_wildcard_to_entire_path: bool = False,
               prefix_with_path: bool = True) -> tp.Iterator[str]:
    """
    Look at given path's files and all subdirectories and return an iterator of
    file names (paths included) that conform to given wildcard.

    Note that wildcard is only applied to the file name if apply_wildcard_to_entire_path is False,
    else the wildcard is applied to entire path (including the application of prefix_with!).

    Files will be additionally prefixed with path, but only if prefix_with_path is True

    :param path: path to look into.
    :param wildcard: a regular expression to match
    :param prefix_with: an optional path component to prefix before the filename with os.path.join
    :param scan_subdirectories: whether to scan subdirectories
    :param apply_wildcard_to_entire_path: whether to take the entire relative path into account
        when checking wildcard
    :param prefix_with_path: whether to add path to the resulting path
    :return: paths with the files. They will be relative paths, relative to path
    """
    if prefix_with_path:
        prefix_with = _cond_join(prefix_with, path)

    for filename in os.listdir(path):
        if scan_subdirectories and os.path.isdir(os.path.join(path, filename)):
            new_prefix = _cond_join(prefix_with, filename)
            yield from find_files(os.path.join(path, filename), wildcard, prefix_with=new_prefix,
                                  prefix_with_path=False)
        else:
            if apply_wildcard_to_entire_path:
                fn_path = _cond_join(prefix_with, filename)
            else:
                fn_path = filename
            if re.match(wildcard, fn_path):
                yield _cond_join(prefix_with, filename)
