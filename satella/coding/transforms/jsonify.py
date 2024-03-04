import enum
import typing as tp

from satella.json import JSONAble


def jsonify(data: tp.Any) -> tp.Optional[tp.Union[str, int, float, list, dict]]:
    """
    Convert any data to a value that's serializable via JSON.

    Objects that are JSONAble will have their to_json() method called.

    Note that enums will be converted to their value.

    As a last resort, str() will be called on the object, and if that fails
    it will have repr() called on it

    :param data: data to convert to a jsonable
    :return: JSON-able data
    """
    if data is None:
        v = None
    elif isinstance(data, (int, float, str)):
        v = data
    elif isinstance(data, enum.Enum):
        v = data.value
    elif isinstance(data, JSONAble):
        v = jsonify(data.to_json())
    elif isinstance(data, tp.Mapping):
        new_mapping = {}
        for key in data:
            new_mapping[jsonify(key)] = jsonify(data[key])
        v = new_mapping
    elif isinstance(data, (tp.Iterable, tp.Iterator)):
        v = [jsonify(elem) for elem in data]
    else:
        try:
            v = str(data)
        except TypeError:
            v = repr(data)
    return v
