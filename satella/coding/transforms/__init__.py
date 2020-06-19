import collections
import typing as tp

__all__ = ['stringify']


def stringify(obj: tp.Union[dict, list], stringifier: tp.Callable[[tp.Any], str] = str) -> tp.Dict[str, str]:
    """
    Stringify all object, ie. put every item and key (if a dict is given) through stringify.

    :param obj: a list or a dict
    :param stringifier: function that accepts any arguments and returns a string representation
    :return: stringified list or a dict
    """
    if isinstance(obj, collections.abc.Mapping):
        return {stringifier(k): stringifier(v) for k, v in obj.items()}
    else:
        return [stringifier(v) for v in obj]

