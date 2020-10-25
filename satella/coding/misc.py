import typing as tp
import warnings
from inspect import Parameter, signature
from queue import Queue

from satella.coding.recast_exceptions import rethrow_as


def queue_iterator(queue: Queue) -> tp.Iterator:
    """
    Syntactic sugar for

    >>> while queue.qsize() > 0:
    >>>     yield queue.get()
    """
    while queue.qsize() > 0:
        yield queue.get()


def update_if_not_none(dictionary: tp.Dict, key: tp.Hashable, value) -> tp.Dict:
    """
    Deprecated alias for :func:`update_key_if_none`
    """
    warnings.warn('This is deprecated and will be removed in Satella 3.0,'
                  'use update_key_if_not_none instead', DeprecationWarning)
    return update_key_if_none(dictionary, key, value)


def source_to_function(src: str) -> tp.Callable[[tp.Any], tp.Any]:
    """
    Transform a string containing a Python expression with a variable x to a lambda.

    It will be treated as if it was appended to 'lambda x: '

    WARNING: Do not run untrusted data. Familiarize yourself with the dangers of passing
    unvalidated data to exec() or eval()!
    """
    q = dict(globals())
    exec('_precond = lambda x: ' + src, q)
    return q['_precond']


def update_attr_if_none(obj: object, attr: str, value: tp.Any,
                        on_attribute_error: bool = True,
                        if_value_is_not_none: bool = False) -> object:
    """
    Updates the object attribute, if it's value is None, or if
    it yields AttributeError (customizable as per on_attribute_error parameter)

    :param obj: object to alter
    :param attr: attribute to set
    :param value: value to set
    :param on_attribute_error: whether to proceed with setting the value on
        AttributeError while trying to read given attribute. If False, AttributeError
        will be raised.
    :param if_value_is_not_none: update object unconditionally, if only value is not None
    :return: obj
    """
    if if_value_is_not_none:
        if value is not None:
            setattr(obj, attr, value)
    else:
        try:
            val = getattr(obj, attr)
            if val is None:
                setattr(obj, attr, value)
        except AttributeError:
            if on_attribute_error:
                setattr(obj, attr, value)
            else:
                raise
    return obj


class _BLANK:
    pass


_BlankType = tp.Type[_BLANK]


def update_key_if_true(dictionary: tp.Dict, key: tp.Hashable, value: tp.Any,
                       flag: tp.Union[bool, _BlankType] = _BLANK) -> tp.Dict:
    """
    If flag is True, execute dictionary[key] = value

    :param dictionary: dictionary to mutate
    :param key: dictionary key to use
    :param value: dictionary value to set
    :param flag: whether to execute the setting operation. If let at default,
        flag will be calculated from boolean of the value
    :return: the dict itself
    """
    if flag is _BLANK:
        flag = bool(value)
    if flag:
        dictionary[key] = value
    return dictionary


@rethrow_as(IndexError, TypeError)
def get_arguments(function: tp.Callable, *args, **kwargs) -> tp.Dict[str, tp.Any]:
    """
    Return local variables that would be defined for given function if called with
    provided arguments.

    :param function: callable to examine
    :param args: arguments to provide
    :param kwargs: keyword arguments to provide
    :return: a dictionary of local variables with their values, as they would
        appear in function if called with provided arguments
    :raise TypeError: the dictionary cannot be created with provided arguments
    """
    sig = signature(function)
    params = sig.parameters.values()
    local_vars = {}

    positionals = [param for param in reversed(params) if
                   param.kind in (Parameter.POSITIONAL_OR_KEYWORD,
                                  Parameter.POSITIONAL_ONLY,
                                  Parameter.VAR_POSITIONAL)]
    args = list(reversed(args))

    params_taken = set()
    print(args, params, positionals)
    while len(positionals) > 0:
        arg = positionals.pop()
        if arg.kind == Parameter.VAR_POSITIONAL:
            local_vars[arg.name] = tuple(reversed(args))
        else:
            v = args.pop()
            print(f'setting {arg.name} to {v}')
            local_vars[arg.name] = v
        params_taken.add(arg.name)

    keywords = [param for param in params if param.kind in (Parameter.POSITIONAL_OR_KEYWORD,
                                                            Parameter.KEYWORD_ONLY,
                                                            Parameter.VAR_KEYWORD) \
                and param.name not in params_taken]

    for keyword in keywords:
        if keyword.kind == Parameter.VAR_KEYWORD:
            local_vars[keyword.name] = kwargs
        else:
            local_vars[keyword.name] = kwargs.pop(keyword.name)

    return local_vars


def update_key_if_none(dictionary: tp.Dict, key: tp.Hashable, value) -> tp.Dict:
    """
    This is deprecated. Please use update_key_if_not_none instead!
    """
    warnings.warn('This is deprecated and will be removed in Satella 3.0, use '
                  'update_key_if_not_none instead', DeprecationWarning)
    return update_key_if_not_none(dictionary, key, value)


def update_key_if_not_none(dictionary: tp.Dict, key: tp.Union[tp.Hashable, tp.Dict],
                           value: tp.Union[tp.Any, _BlankType] = _BLANK) -> tp.Dict:
    """
    Syntactic sugar for

    >>> if value is not None:
    >>>     dictionary[key] = value

    If value is passed, else

    >>> for key, value in key.items():
    >>>     if value is not None:
    >>>         dictionary[key] = value

    :param dictionary: dictionary to update
    :param key: key to use or a dictionary of items
    :param value: value to use
    :return: the dictionary itself
    """
    if value is _BLANK:
        for key, val in key.items():
            if val is not None:
                dictionary[key] = val
    elif value is not None:
        dictionary[key] = value
    return dictionary
