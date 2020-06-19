import collections
import typing as tp

__all__ = ['stringify']


def stringify(obj: tp.Union[tp.Any], stringifier: tp.Callable[[tp.Any], str] = str,
              recursively: bool = False) -> tp.Dict[str, str]:
    """
    Stringify all object:

    ie. if a dict, put every item and key (if a dict is given) through stringify.
        if a list, put every item through stringify
        else just call stringify on it

    :param obj: a list or a dict
    :param stringifier: function that accepts any arguments and returns a string representation
    :param recursively: whether to recursively stringify elements, ie. stringify will be called on all the children
    :return: stringified object
    """
    if isinstance(obj, collections.abc.Mapping):
        if recursively:
            stringifier = lambda obj2: stringify(obj2, stringifier=stringifier, recursively=True)
        return {stringifier(k): stringifier(v) for k, v in obj.items()}
    elif isinstance(obj, collections.abc.Sequence):
        if recursively:
            stringifier = lambda obj2: stringify(obj2, stringifier=stringifier, recursively=True)
        return [stringifier(v) for v in obj]
    else:
        return stringifier(obj)

