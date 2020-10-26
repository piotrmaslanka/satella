import typing as tp

from satella.json import JSONAble


def jsonify(data: tp.Any) -> tp.Optional[tp.Union[str, int, float, list, dict]]:
    """
    Convert any data to a value that's serializable via JSON.

    Objects that are JSONAble will have their to_json() method called.

    As a last resort, str() will be called on the object, and if that fails
    it will have repr() called on it

    :param data: data to convert to a jsonable
    :return: JSON-able data
    """
    if data is None:
        return None
    elif isinstance(data, (int, float, str)):
        return data
    elif isinstance(data, JSONAble):
        return jsonify(data.to_json())
    elif isinstance(data, tp.Mapping):
        new_mapping = {}
        for key in data:
            new_mapping[jsonify(key)] = jsonify(data[key])
        return new_mapping
    elif isinstance(data, (tp.Iterable, tp.Iterator)):
        return [jsonify(elem) for elem in data]
    else:
        try:
            return str(data)
        except TypeError:
            return repr(data)