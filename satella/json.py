import json
import typing as tp
from abc import ABCMeta, abstractmethod

__all__ = ['JSONEncoder', 'JSONAble', 'json_encode']


class JSONAble(metaclass=ABCMeta):
    @abstractmethod
    def to_json(self) -> tp.Union[list, dict, str, int, float, None]:
        """Return a JSON-able representation of this object"""


class JSONEncoder(json.JSONEncoder):
    def default(self, o) -> str:
        if hasattr(o, 'to_json'):
            return o.to_json()
        return super().default(o)


def json_encode(x) -> str:
    """
    Convert an object to JSON. Will properly handle subclasses of JSONAble

    :param x: object to convert
    """
    return JSONEncoder().encode(x)
