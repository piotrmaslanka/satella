import json
import typing as tp
from abc import ABCMeta, abstractmethod

import typing

from satella.coding.typing import NoneType

try:
    import ujson
except ImportError:
    pass

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
    """

    def default(self, o: tp.Any) -> Jsonable:
        if hasattr(o, 'to_json'):
            return o.to_json()
        elif isinstance(o, (int, float, str, NoneType)):
            return o
        elif isinstance(o, (list, tuple)):
            return [self.default(v) for v in o]
        elif isinstance(o, dict):
            return {self.default(k): self.default(v) for k, v in o.items()}

        try:
            return super().default(o)
        except TypeError:
            dct = {}
            try:
                for k, v in o.__dict__.items():
                    dct[k] = self.default(v)
            except AttributeError:  # o has no attribute '__dict__', try with slots
                try:
                    for slot in o.__slots__:
                        dct[slot] = self.default(getattr(o, slot))
                except AttributeError:      # it doesn't have __slots__ either?
                    return '<an instance of %s>' % (o.__class__.__name__, )
            return dct


def json_encode(x: tp.Any) -> str:
    """
    Convert an object to JSON. Will properly handle subclasses of JSONAble

    :param x: object to convert
    """
    return JSONEncoder().encode(x)


def write_json_to_file(path: str, value: JSONAble) -> None:
    """
    Write out a JSON to a file as UTF-8 encoded plain text.

    :param path: path to the file
    :param value: JSON-able content
    """
    if isinstance(value, JSONAble):
        value = value.to_json()
    with open(path, 'w') as f_out:
        try:
            ujson.dump(value, f_out)
        except NameError:
            json.dump(value, f_out)


def write_json_to_file_if_different(path: str, value: JSONAble) -> bool:
    """
    Read JSON from a file. Write out a JSON to a file if it's value is different,
    as UTF-8 encoded plain text.

    :param path: path to the file
    :param value: JSON-able content
    :return: whether the write actually happened
    """
    if isinstance(value, JSONAble):
        value = value.to_json()
    try:
        val = read_json_from_file(path)
        if val != value:
            write_json_to_file(path, value)
            return True
        return False
    except (OSError, ValueError):
        write_json_to_file(path, value)
        return True


def read_json_from_file(path: str) -> JSONAble:
    """
    Load a JSON from a provided file, as UTF-8 encoded plain text.

    :param path: path to the file
    :return: JSON content
    :raises ValueError: the file contained an invalid JSON
    :raises OSError: the file was not readable or did not exist
    """
    try:
        with open(path, 'r') as f_in:
            return ujson.load(f_in)
    except NameError:
        with open(path, 'r') as f_in:
            try:
                return json.load(f_in)
            except json.decoder.JSONDecodeError as e:
                raise ValueError(str(e))
