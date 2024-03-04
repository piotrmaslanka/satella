from __future__ import annotations

import codecs
import functools
import io
import os
import re
import shutil
import typing as tp

__all__ = ['read_re_sub_and_write', 'find_files', 'split', 'read_in_file', 'write_to_file',
           'write_out_file_if_different', 'make_noncolliding_name', 'try_unlink',
           'DevNullFilelikeObject', 'read_lines', 'AutoflushFile']

from satella.coding import wraps
from satella.coding.recast_exceptions import silence_excs, reraise_as
from satella.coding.structures import Proxy
from satella.coding.typing import Predicate

SEPARATORS = {'\\', '/'}
SEPARATORS.add(os.path.sep)


def value_error_on_closed_file(getter):
    def outer(fun):
        @functools.wraps(fun)
        def inner(self, *args, **kwargs):
            if getter(self):
                raise ValueError('File closed')
            return fun(self, *args, **kwargs)

        return inner

    return outer


closed_devnull = value_error_on_closed_file(lambda y: y.is_closed)


class DevNullFilelikeObject(io.FileIO):
    """
    A /dev/null filelike object. For multiple uses.

    :param binary: is this a binary file
    """

    def __init__(self, binary: bool = False):
        self.is_closed = False
        self.binary = binary

    @closed_devnull
    def tell(self) -> int:
        """
        Return the current file offset

        :return: the current file offset
        """
        return 0

    @closed_devnull
    def truncate(self, __size: tp.Optional[int] = None) -> int:
        """Truncate file to __size starting bytes"""
        return 0

    @closed_devnull
    def writable(self) -> bool:
        """Is this object writable"""
        return True

    @closed_devnull
    def seek(self, v: int) -> int:
        """Seek to a particular file offset"""
        return 0

    @closed_devnull
    def seekable(self) -> bool:
        """Is this file seekable?"""
        return True

    @closed_devnull
    def read(self, byte_count: tp.Optional[int] = None) -> tp.Union[str, bytes]:
        """
        :raises ValueError: this object has been closed
        :raises io.UnsupportedOperation: since reading from this is forbidden
        """
        return b'' if self.binary else ''

    @closed_devnull
    def write(self, y: tp.Union[str, bytes]) -> int:
        """
        Discard any amount of bytes.

        This will raise a RuntimeWarning warning upon writing invalid type.

        :raises ValueError: this object has been closed
        :raises TypeError: eg. type set to binary and text provided to write
        :return: length of written content
        """
        if not isinstance(y, str) and not self.binary:
            raise TypeError(f'Expected text data, but got {type(y)}')
        elif not isinstance(y, bytes) and self.binary:
            raise TypeError(f'Expected binary data, but got {type(y)}')
        return len(y)

    @closed_devnull
    def flush(self) -> None:
        """
        :raises ValueError: when this object has been closed
        """

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


is_closed_getter = value_error_on_closed_file(lambda y: y.__dict__['closed'])


def close_file_after(fun):
    @wraps(fun)
    def inner(self, *args, **kwargs):
        try:
            return fun(self, *args, **kwargs)
        finally:
            self._close_file()

    return inner


class AutoflushFile(Proxy[io.FileIO]):
    """
    A file that is supposed to be closed after each write command issued.

    The file will be open only when there's an action to do on it called.

    Best for appending so that other processes can read.

    Use like:

    >>> f = AutoflushFile('test.txt', 'rb+', encoding='utf-8')
    >>> f.write('test')
    >>> with open('test.txt', 'a+', encoding='utf-8') as fin:
    >>>     assert fin.read() == 'test'
    """

    def __init__(self, file: str, mode: str, *con_args, **con_kwargs):
        """
        :param file: path to the file
        :param mode: mode to open the file with. Allowed values are w, wb, w+, a+, wb+, ab+, a, ab.
            w+ and wb+ will truncate the file. Effective mode will be chosen by the class whatever just makes sense.
        :raises ValueError: invalid mode chosen
        """
        self.__dict__['con_kwargs'] = con_kwargs
        self.__dict__['pointer'] = None
        self.__dict__['closed'] = False

        if mode in ('w', 'w+', 'wb+', 'wb'):
            fle = open(*(file, 'wb'))
            fle.truncate(0)
            fle.close()

        with reraise_as(KeyError, ValueError, f'Unsupported mode "{mode}"'):
            mode = {'w': 'a', 'wb': 'ab', 'w+': 'a+', 'wb+': 'ab+', 'a': 'a', 'ab': 'ab'}[mode]

        self.__dict__['con_args'] = file, mode, *con_args

        fle = self._open_file()
        super().__init__(fle)
        self.__dict__['pointer'] = fle.tell()
        self._close_file()

    @is_closed_getter
    @close_file_after
    def seek(self, offset: int, whence: int = os.SEEK_SET) -> int:
        """
        Seek to a provided position within the file

        :param offset: offset to seek file
        :param whence: how to count. Refer to documentation of file.seek()

        :return: current pointer
        """
        fle = self._open_file()
        v = fle.seek(offset, whence)
        self.__dict__['pointer'] = fle.tell()
        return v

    @is_closed_getter
    @close_file_after
    def read(self, *args, **kwargs) -> tp.Union[str, bytes]:
        """
        Read a file, returning the read-in data

        :return: data readed
        """
        fle = self._open_file()
        p = fle.read(*args, **kwargs)
        self.__dict__['pointer'] = fle.tell()
        return p

    def _get_file(self) -> tp.Optional[AutoflushFile]:
        return self.__dict__.get('_Proxy__obj')

    @is_closed_getter
    @close_file_after
    def readall(self) -> tp.Union[str, bytes]:
        """Read all contents into the file"""
        fle = self._open_file()
        return fle.readall()

    def _open_file(self) -> io.FileIO:
        file = self._get_file()
        if file is None:
            file = open(*self.con_args, **self.con_kwargs)
            ptr = file.tell()
            self.__dict__['_Proxy__obj'] = file
            self.__dict__['pointer'] = ptr
        return file

    def _close_file(self) -> None:
        file = self._get_file()
        if file is not None:
            ptr = file.tell()
            self.__dict__['pointer'] = ptr
            file.close()
            self.__dict__['_Proxy__obj'] = None

    @is_closed_getter
    @close_file_after
    def close(self) -> None:
        """
        Closes the file.
        """
        self.__dict__['closed'] = True

    @is_closed_getter
    @close_file_after
    def write(self, *args, **kwargs) -> int:
        """
        Write a particular value to the file, close it afterwards.

        :return: amount of bytes written
        """
        fle = self._open_file()
        val = fle.write(*args, **kwargs)
        self.__dict__['pointer'] = fle.tell()
        return val

    @is_closed_getter
    @close_file_after
    def truncate(self, _size: tp.Optional[int] = None) -> int:
        """Truncate file to __size starting bytes"""
        fle = self._open_file()
        v = fle.truncate(_size)
        self.__dict__['pointer'] = fle.tell()
        return v
