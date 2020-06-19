import collections
import typing as tp

__all__ = ['stringify']


def stringify(obj: tp.Union[tp.Any], stringifier: tp.Callable[[tp.Any], str] = str,
              recursively: bool = False,
              str_none: bool = False) -> tp.Dict[str, str]:
    """
    Stringify all object:

    ie. if a dict, put every item and key (if a dict is given) through stringify.
        if a list, put every item through stringify
        else just call stringify on it.

        Note that if you use recursively, then dicts and lists are allowed to be valid elements of the returned
        representation!

    :param obj: a list or a dict
    :param stringifier: function that accepts any arguments and returns a string representation
    :param recursively: whether to recursively stringify elements, ie. stringify will be called on all the children
    :param str_none: whether to return None if given a None. If True, "None" will be returned instead
    :return: stringified object
    """
    if isinstance(obj, collections.abc.Mapping):
        make_str = (lambda obj2: stringify(obj2, stringifier, True)) if recursively else stringifier
        return {make_str(k): make_str(v) for k, v in obj.items()}
    elif isinstance(obj, collections.abc.Sequence):
        make_str = (lambda obj2: stringify(obj2, stringifier, True)) if recursively else stringifier
        return [make_str(v) for v in obj]
    elif obj is None:
        if str_none:
            return stringifier(None)
        else:
            return None
    else:
        return stringifier(obj)
