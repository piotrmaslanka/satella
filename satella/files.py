import codecs
import io
import os
import re
import shutil
import typing as tp

__all__ = ['read_re_sub_and_write', 'find_files', 'split', 'read_in_file', 'write_to_file',
           'write_out_file_if_different', 'make_noncolliding_name', 'try_unlink',
           'DevNullFilelikeObject', 'read_lines']

from satella.coding.recast_exceptions import silence_excs
from satella.coding.typing import Predicate

SEPARATORS = {'\\', '/'}
SEPARATORS.add(os.path.sep)


class DevNullFilelikeObject:
    """
    A /dev/null filelike object. For multiple uses.
    """
    __slots__ = ('is_closed',)

    def __init__(self):
        self.is_closed = False

    def read(self, byte_count: tp.Optional[int] = None):
        """
        :raises ValueError: this object has been closed
        :raises io.UnsupportedOperation: since reading from this is forbidden
        """
        if self.is_closed:
            raise ValueError('Reading from closed /dev/null!')
        raise io.UnsupportedOperation('read')

    def write(self, x: tp.Union[str, bytes]) -> int:
        """
        Discard any amount of bytes

        :raises ValueError: this object has been closed
        :return: length of written content
        """
        if self.is_closed:
            raise ValueError('Writing to closed /dev/null!')
        return len(x)

    def flush(self) -> None:
        """
        :raises ValueError: when this object has been closed
        """
        if self.is_closed:
            raise ValueError('flush of closed file')

    def close(self) -> None:
        """
        Close this stream. Further write()s and flush()es will raise a ValueError.
        No-op if invoked multiple times
        """
        self.is_closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def _has_separator(path: str) -> bool:
    # handle Windows case
    if len(path) == 3:
        if path.endswith(':/') or path.endswith(':\\'):
            return False
    return any(map(lambda x: x in path, SEPARATORS))


def read_lines(path: str, delete_empty_lines: bool = True,
               encoding: str = 'utf-8') -> tp.List[str]:
    """
    Read lines from a particular file, removing end-of-line characters and optionally
    empty lines. Additionally whitespaces (and end-of-line characters) will be removed
    from both ends of each line.

    :param path: path of file to read
    :param delete_empty_lines: set to False if empty lines are not to be removed
    :param encoding: encoding to read the file with
    :return: each line as a separate entry
    """
    with codecs.open(path, 'r', encoding) as f_in:
        lines = [line.strip() for line in f_in.readlines()]
    if delete_empty_lines:
        lines = [line for line in lines if line]
    return lines


def make_noncolliding_name(path: str,
                           exists_checker: Predicate[str] = os.path.exists) -> str:
    """
    Try to make a noncolliding name in such a way that .1, .2, .3, and so on will be appended
    to the file name right before the extension (yielding test.1.txt) or at the end of the file
    name if the extension isn't present

    :param path: path of the file that has not to exist
    :param exists_checker: a callable to check with if the file exists
    :return: name mutated in such a way that exists_checker returned False on it
    """
    path, filename = os.path.split(path)
    if '.' in filename:
        *filename, extension = filename.split('.')
        filename = '.'.join(filename)
        extension = '.' + extension
    else:
        extension = ''
    addition = ''
    addition_counter = 0
    while exists_checker(os.path.join(path, filename + addition + extension)):
        addition_counter += 1
        addition = '.' + str(addition_counter)
    return os.path.join(path, filename + addition + extension)


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


def write_to_file(path: str, data: tp.Union[bytes, str],
                  encoding: tp.Optional[str] = None) -> None:
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


class _NOTSET:
    ...


def read_in_file(path: str, encoding: tp.Optional[str] = None,
                 default: tp.Optional[tp.Union[bytes, str]] = _NOTSET) -> tp.Union[bytes, str]:
    """
    Opens a file for reading, reads it in, converts to given encoding (or returns as bytes
    if not given), and closes it.

    :param path: path of file to read
    :param encoding: optional encoding. If default, this will be returned as bytes
    :param default: value to return when the file does not exist. Default (None) will raise a
        FileNotFoundError
    :return: file content, either decoded as a str, or not as bytes
    :raises FileNotFoundError: file did not exist and default was not set
    """
    if os.path.isdir(path):
        if default is not _NOTSET:
            return default
        raise FileNotFoundError('%s found and is a directory' % (path,))

    try:
        if encoding is None:
            file = open(path, 'rb')
        else:
            file = codecs.open(path, 'r', encoding)
    except FileNotFoundError:
        if default is not _NOTSET:
            return default
        raise

    try:
        return file.read()
    finally:
        file.close()


def read_re_sub_and_write(path: str, pattern: tp.Union[re.compile, str],
                          repl: tp.Union[tp.Callable[[tp.Any], str]]) -> None:
    """
    Read a text file, treat with re.sub and write the contents.

    Note that this is not thread or multiprocess safe.

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


@silence_excs(OSError, returns=False)
def try_unlink(path: str) -> bool:
    """
    A syntactic sugar for:

    >>> try:
    >>>     os.unlink(path)
    >>>     return True
    >>> except FileNotFoundError:
    >>>     return False

    Note that if path is a directory, rmtree from shlex will be called on it, and
    any OSErrors will report the deletion as False

    :param path: path of file to delete
    :return: whether the deletion happened
    """
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.unlink(path)
    return True


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

    Note that wildcard is only applied to the file name if apply_wildcard_to_entire_path
    is False, else the wildcard is applied to entire path (including the application of
    prefix_with!).

    Files will be additionally prefixed with path, but only if prefix_with_path is True

    .. warning:: Note that this will try to match only the start of the path. For a complete match
        remember to put a $ at the end of the string!

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
            yield from find_files(os.path.join(path, filename), wildcard,
                                  prefix_with=new_prefix,
                                  prefix_with_path=False)
        else:
            if apply_wildcard_to_entire_path:
                fn_path = _cond_join(prefix_with, filename)
            else:
                fn_path = filename
            if re.match(wildcard, fn_path):
                yield _cond_join(prefix_with, filename)


def write_out_file_if_different(path: str, data: tp.Union[bytes, str],
                                encoding: tp.Optional[str] = None) -> bool:
    """
    Syntactic sugar for

    >>> try:
    >>>     if read_in_file(path, encoding) != data:
    >>>         write_to_file(path, data, encoding)
    >>>         return True
    >>>     else:
    >>>         return False
    >>> except OSError:
    >>>     write_to_file(path, data, encoding)
    >>>     return True

    :param path: Path to put the file under
    :param data: Data to write. Must be bytes if no encoding is given, str otherwise
    :param encoding: Encoding. Default is None, which means no encoding (bytes will be written)
    :return: if write has happened
    """
    try:
        if read_in_file(path, encoding) != data:
            write_to_file(path, data, encoding)
            return True
        else:
            return False
    except FileNotFoundError:
        write_to_file(path, data, encoding)
        return True
