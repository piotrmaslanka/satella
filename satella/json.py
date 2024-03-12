import enum
import json
import typing as tp
import warnings
from abc import ABCMeta, abstractmethod

from satella.coding.typing import NoneType
from satella.files import write_out_file_if_different

__all__ = ['JSONEncoder', 'JSONAble', 'json_encode', 'read_json_from_file',
           'write_json_to_file', 'write_json_to_file_if_different']

Jsonable = tp.TypeVar('Jsonable', list, dict, str, int, float, None)


class JSONAble(metaclass=ABCMeta):
    __slots__ = ()

    @abstractmethod
    def to_json(self) -> Jsonable:
        """Return a JSON-able representation of this object"""


class JSONEncoder(json.JSONEncoder):
    """
    This encoder will encode everything!

    enums will be dumped to their value.
    """

    def default(self, o: tp.Any) -> Jsonable:
        if hasattr(o, 'to_json'):
            v = o.to_json()
        elif isinstance(o, (int, float, str, NoneType)):
            v = o
        elif isinstance(o, enum.Enum):
            v = o.value
        elif isinstance(o, (list, tuple)):
            v = [self.default(v) for v in o]
        elif isinstance(o, dict):
            v = {self.default(k): self.default(v) for k, v in o.items()}
        else:
            try:
                v = super().default(o)
            except TypeError:
                v = {}
                try:
                    for k, val in o.__dict__.items():
                        v[k] = self.default(val)
                except AttributeError:  # o has no attribute '__dict__', try with slots
                    try:
                        for slot in o.__slots__:
                            v[slot] = self.default(getattr(o, slot))
                    except AttributeError:  # it doesn't have __slots__ either?
                        v = '<an instance of %s>' % (o.__class__.__name__,)
        return v


def json_encode(x: tp.Any) -> str:
    """
    Convert an object to JSON. Will properly handle subclasses of JSONAble

    :param x: object to convert
    """
    return JSONEncoder().encode(x)


def write_json_to_file(path: str, value: JSONAble, **kwargs) -> None:
    """
    Write out a JSON to a file as UTF-8 encoded plain text.

    This will use Satella's :class:`~satella.json.JSONEncoder` internally.

    :param path: path to the file
    :param value: JSON-able content
    :param kwargs: Legacy argument do not use it, will raise a warning upon non-empty. This never did anything.
    """
    if kwargs:
        warnings.warn('Do not use kwargs, it has no effect', DeprecationWarning)
    with open(path, 'w') as f_out:
        f_out.write(JSONEncoder().encode(value))


def write_json_to_file_if_different(path: str, value: JSONAble,
                                    encoding: str = 'utf-8', **kwargs) -> bool:
    """
    Read JSON from a file. Write out a JSON to a file if it's value is different,
    as UTF-8 encoded plain text.

    This will use Satella's :class:`~satella.json.JSONEncoder` internally.

    :param path: path to the file
    :param value: JSON-able content
    :param encoding: encoding to use while parsing the contents of the file
    :param kwargs: will be passed to ujson/json dumps
    :return: whether the write actually happened
    """
    value = JSONEncoder().encode(value)
    return write_out_file_if_different(path, value, encoding)


def read_json_from_file(path: str) -> JSONAble:
    """
    Load a JSON from a provided file, as UTF-8 encoded plain text.

    :param path: path to the file
    :return: JSON content
    :raises ValueError: the file contained an invalid JSON
    :raises OSError: the file was not readable or did not exist
    """
    try:
        import ujson
        with open(path, 'r') as f_in:
            v = ujson.load(f_in)
    except ImportError:
        with open(path, 'r') as f_in:
            try:
                v = json.load(f_in)
            except json.decoder.JSONDecodeError as e:
                raise ValueError(str(e))
    return v
