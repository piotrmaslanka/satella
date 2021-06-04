import codecs
import os
import re
import typing as tp

from satella.exceptions import ConfigurationValidationError
from .base import Descriptor, ConfigDictValue
from .registry import register_custom_descriptor


@staticmethod
def _make_boolean(v: tp.Any) -> bool:
    if isinstance(v, str):
        if v.upper() == 'TRUE':
            return True
        elif v.upper() == 'FALSE':
            return False
        else:
            raise ConfigurationValidationError('Unknown value of "%s" posing to be a bool'
                                               % (v,))
    else:
        return bool(v)


@register_custom_descriptor('bool')
class Boolean(Descriptor):
    """
    This value must be a boolean, or be converted to one
    """
    BASIC_MAKER = _make_boolean


@register_custom_descriptor('int')
class Integer(Descriptor):
    """
    This value must be an integer, or be converted to one
    """
    BASIC_MAKER = int


@register_custom_descriptor('float')
class Float(Descriptor):
    """
    This value must be a float, or be converted to one
    """
    BASIC_MAKER = float


@register_custom_descriptor('str')
class String(Descriptor):
    """
    This value must be a string, or be converted to one
    """
    BASIC_MAKER = str


class FileObject:
    """
    What you get for values in schema of :class:`~satella.configuration.schema.File`.

    This object is comparable and hashable, and is equal to the string of it's path
    """
    __slots__ = 'path',

    def __init__(self, path: str):
        self.path = path

    def __repr__(self):
        return '<File object %s>' % (self.path,)

    def __str__(self):
        return self.path

    def __eq__(self, other) -> bool:
        return self.path == str(other) and isinstance(other, FileObject)

    def __hash__(self) -> int:
        return hash(self.path)

    def get_value(self, encoding: tp.Optional[str] = None) -> tp.Union[str, bytes]:
        """
        Read in the entire file into memory

        :param encoding: optional encoding to apply. If None given, bytes will be returned
        :return: file contents
        """
        with open(self.path, 'rb') as f_in:
            data = f_in.read()
        if encoding:
            return data.decode(encoding)
        else:
            return data

    def open(self, mode: str):
        """
        Open the file in specified mode

        :param mode: mode to open the file in
        :return: file handle
        """
        return open(self.path, mode)


class DirectoryObject:
    """
    What you get for values in schema of :class:`~satella.configuration.schema.Directory`.

    This object is comparable and hashable, and is equal to the string of it's path
    """
    __slots__ = 'path',

    def __init__(self, path: str):
        self.path = path

    def __repr__(self):
        return '<Directory object %s>' % (self.path,)

    def __str__(self):
        return self.path

    def __eq__(self, other) -> bool:
        return self.path == str(other) and isinstance(other, DirectoryObject)

    def __hash__(self) -> int:
        return hash(self.path)

    def get_files(self) -> tp.Iterable[str]:
        """
        Return a list of files inside this directory
        :return:
        """
        return os.listdir(self.path)


@staticmethod
def _make_file(v: str) -> bool:
    if not os.path.isfile(v):
        raise ConfigurationValidationError('Expected to find a file under %s'
                                           % (v,))
    return FileObject(v)


@register_custom_descriptor('file')
class File(Descriptor):
    """
    This value must be a valid path to a file. The value in your schema will be
    an instance of :class:`~satella.configuration.schema.basic.FileObject`
    """

    BASIC_MAKER = _make_file


@register_custom_descriptor('file_contents')
class FileContents(Descriptor):
    """
    This value must be a valid path to a file. The value in your schema will be
    the contents of this file, applied with encoding (if given). By default, bytes will be read in
    """

    def __init__(self, encoding: tp.Optional[str] = None, strip_afterwards: bool = False):
        super().__init__()
        self.encoding = encoding
        self.strip_afterwards = strip_afterwards

    def BASIC_MAKER(self, c: str):
        if not self.encoding:
            with open(c, 'rb') as f_in:
                y = f_in.read()
        else:
            with codecs.open(c, 'r', encoding=self.encoding) as f_in:
                y = f_in.read()

        if self.strip_afterwards:
            y = y.strip()
        return y


@staticmethod
def _make_directory(v: str) -> bool:
    if not os.path.isdir(v):
        raise ConfigurationValidationError('Expected to find a directory under %s'
                                           % (v,))
    return DirectoryObject(v)


@register_custom_descriptor('dir')
class Directory(Descriptor):
    """
    This value must be a valid path to a file. The value in your schema will be
    an instance of :class:`~satella.configuration.schema.basic.FileObject`
    """

    BASIC_MAKER = _make_directory


class Regexp(String):
    """
    Base class for declaring regexp-based descriptors. Overload it's attribute REGEXP. Use as
    following:

    >>> class IPv6(Regexp):
    >>>     REGEXP = '(([0-9a-f]{1,4}:)' ...
    """
    __slots__ = ('regexp',)

    REGEXP = r'.*'

    def __init__(self):
        super().__init__()
        if isinstance(self.REGEXP, str):
            self.regexp = re.compile(self.REGEXP)
        else:
            self.regexp = self.REGEXP

    def __call__(self, value: ConfigDictValue) -> str:
        value = super(Regexp, self).__call__(value)

        match = self.regexp.match(value)
        if not match:
            raise ConfigurationValidationError('value does not match %s' % (self.REGEXP.pattern,),
                                               value)

        return match.group(0)

    def __str__(self):
        return 'Regexp(%s)' % (self.REGEXP.pattern,)


@register_custom_descriptor('ipv4')
class IPv4(Regexp):
    """
    This must be a valid IPv4 address (no hostnames allowed)
    """
    REGEXP = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
