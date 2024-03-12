import enum
import typing as tp
import warnings
from inspect import Parameter, signature
from queue import Empty
from queue import Queue

from satella.coding.recast_exceptions import rethrow_as


def enum_value(value):
    """
    If value is an enum, extract and return it's value.

    Otherwise, return it as-is.

    :param value: value to extract enum from
    :return: value
    """
    if isinstance(value, enum.Enum):
        return value.value
    return value


def length(lenable) -> int:
    """
    Return length of an item. If it is a generator, exhaust it and return it's length.
    """
    try:
        return len(lenable)
    except TypeError:
        i = 0
        for _ in lenable:
            i += 1
        return i


def contains(needle, haystack) -> bool:
    """
    A syntactic sugar for the following:

    >>> for item in haystack:
    >>>     if needle == item:
    >>>         return True
    >>> return False

    Note that this is very like Python's in operator, however it's not quite same, since
    in doesn't involve the __eq__ operator at every step!

    This function for example allows you to circumvent Python's limitations concerning
    :class:`~satella.coding.structures.ComparableEnum`

    :param needle: needle to check for
    :param haystack: haystack to check against
    :return: whether haystack contains the element
    """
    for item in haystack:
        if needle == item:
            return True
    return False


class Closeable:
    """
    A class that needs to clean up its own resources.

    It's destructor calls .close(). Use like this:

    >>> class MyClose(Closeable):
    >>>     def close(self):
    >>>         if super().close():
    >>>             .. clean up ..

    Can be also used as a context manager, with close() called upon __exit__.

    .. warning:: You should extend both __init__ and close(). Invoke __init__() at the end of
        your class constructor, this will prevent the destructor from closing on half-initialized
        classes.

    Objects before initialization (calling of this constructor) are considered closed.
    Checking if they are closed will emit a warning.
    """
    __slots__ = '__finalized',

    def __init__(self):
        self.__finalized = False

    @property
    def closed(self) -> bool:
        """
        :return: whether this object is closed
        """
        try:
            return self.__finalized
        except AttributeError:
            warnings.warn('You are checking whether a non-initialized object was closed',
                          UserWarning)
            return True

    def close(self) -> bool:
        """
        Check if the resource needs cleanup, and clean up this resource.

        Use like this:

        >>> class MyClose(Closeable):
        >>>     def close(self):
        >>>         if super().close():
        >>>             .. clean up ..

        :return: whether the cleanup should proceed
        :raises RuntimeError: the constructor was not invoked
        """
        try:
            return not self.__finalized
        except AttributeError:
            warnings.warn('Attempted to clean up a non-initialized object', UserWarning)
        finally:
            self.__finalized = True

    def __del__(self) -> None:
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def queue_iterator(queue: Queue) -> tp.Iterator:
    """
    Syntactic sugar for

    >>> while queue.qsize() > 0:
    >>>     yield queue.get()
    """
    while queue.qsize() > 0:
        try:
            yield queue.get(block=False)
        except Empty:
            return


def update_if_not_none(dictionary: tp.Dict, key: tp.Hashable, value) -> tp.Dict:
    """
    Deprecated alias for :func:`update_key_if_none`

    .. deprecated:: 2.14.22
    """
    warnings.warn('This is deprecated and will be removed in Satella 3.0,'
                  'use update_key_if_not_none instead', DeprecationWarning)
    return update_key_if_none(dictionary, key, value)


def chain_callables(callable1: tp.Callable, callable2: tp.Callable) -> tp.Callable:
    """
    Link two callables together. callable2, if it takes an argument, will receive
    callables'1 result, and if it takes no arguments it will received nothing.

    :param callable1: first callable to call
    :param callable2: callable to call with callable1's result
    :return: result of callable2
    """

    def inner(*args, **kwargs):
        res = callable1(*args, **kwargs)
        try:
            res = callable2(res)
        except TypeError as e:
            if 'positional arguments but' in e.args[0] and 'was given' in e.args[0] and 'takes' in e.args[0]:
                res = callable2()
            else:
                raise
        return res

    return inner


def source_to_function(src: tp.Union[tp.Callable, str]) -> tp.Callable[[tp.Any], tp.Any]:
    """
    If src is callable, return it as-is
    Transform a string containing a Python expression with a variable x to a lambda.

    It will be treated as if it was appended to 'lambda x: '

    WARNING: Do not run untrusted data. Familiarize yourself with the dangers of passing
    unvalidated data to exec() or eval()!

    :param src: a callable or a Python string expression
    :return: a callable
    """
    if isinstance(src, str):
        q = dict(globals())
        exec('_precond = lambda x: ' + src, q)
        return q['_precond']
    return src


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
            if not on_attribute_error:
                raise
            setattr(obj, attr, value)
    return obj


class _BLANK:       # pylint: disable=too-few-public-methods
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


def get_arguments(function: tp.Callable, *args, **kwargs) -> tp.Dict[str, tp.Any]:
    """
    Return local variables that would be defined for given function if called with
    provided arguments.

    Note that this function will not return the "self" argument of methods
    and it won't return the class of "cls" of classmethods.

    :param function: callable to examine
    :param args: arguments to provide
    :param kwargs: keyword arguments to provide
    :return: a dictionary of local variables with their values, as they would
        appear in function if called with provided arguments
    :raise TypeError: the dictionary cannot be created with provided arguments
    """
    return _get_arguments(function, False, *args, **kwargs)


# pylint: disable=too-many-locals
@rethrow_as(IndexError, TypeError)
def _get_arguments(function: tp.Callable, special_behaviour: bool, *args, **kwargs):
    """
    :param special_behaviour: enable special behaviour to be used in for_arguments
    """
    sig = signature(function)
    params = sig.parameters.values()
    local_vars = {}

    positionals = [param for param in reversed(params) if
                   param.kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.POSITIONAL_ONLY, Parameter.VAR_POSITIONAL)]
    args = list(reversed(args))

    arguments_left = set(param.name for param in params)
    while positionals:
        arg = positionals.pop()
        arg_kind = arg.kind
        arg_name = arg.name
        if arg_kind == Parameter.VAR_POSITIONAL and not special_behaviour:
            local_vars[arg_name] = tuple(reversed(args))
        else:
            try:
                v = args.pop()
                arguments_left.remove(arg_name)
            except IndexError:
                try:
                    if arg.default != Parameter.empty:
                        raise AttributeError()
                    break
                except (AttributeError, TypeError):
                    v = arg.default
            local_vars[arg_name] = v

    keywords = [param for param in params if param.kind in (Parameter.POSITIONAL_OR_KEYWORD,
                                                            Parameter.KEYWORD_ONLY,
                                                            Parameter.VAR_KEYWORD)
                and param.name in arguments_left]

    for keyword in keywords:
        keyword_name = keyword.name
        if keyword.kind == Parameter.VAR_KEYWORD and not special_behaviour:
            local_vars[keyword_name] = kwargs
            continue
        try:
            v = kwargs.pop(keyword_name)
        except KeyError:
            try:
                if Parameter.empty == keyword.default:
                    if not special_behaviour:
                        raise TypeError('Not enough keyword arguments')
                    v = None
                else:
                    v = keyword.default
            except (AttributeError, TypeError):
                continue  # comparison was impossible

        local_vars[keyword_name] = v

    for param in params:
        param_name = param.name
        if param_name not in local_vars:
            if not special_behaviour:
                raise TypeError('Not enough keyword arguments')
            local_vars[param_name] = None

    return local_vars


def call_with_arguments(function: tp.Callable, arguments: tp.Dict[str, tp.Any]) -> tp.Any:
    """
    Call a function, but with giving it arguments via a dictionary.

    Dictionary should be a mapping of argument name to it's value.

    :param function: function to call
    :param arguments:
        a dict of arguments : argument name => argument value.
        This dictionary will be modified!
    :return: return value of the function
    :raise TypeError: too few arguments, or some arguments required were missing
    :raise ValueError: too many arguments given
    """
    args = []
    kwargs = {}
    for param in signature(function).parameters.values():
        param_name = param.name
        param_kind = param.kind
        if param_name not in arguments:
            if param_kind in (Parameter.VAR_KEYWORD, Parameter.VAR_POSITIONAL):
                continue
            elif param.default == Parameter.empty:
                raise TypeError('Argument %s not found' % (param_name,))
            continue

        if param_kind == Parameter.POSITIONAL_ONLY or param_kind == Parameter.POSITIONAL_OR_KEYWORD:
            args.append(arguments.pop(param_name))
        elif param_kind == Parameter.VAR_POSITIONAL:
            args.extend(arguments.pop(param_name))
        elif param_kind == Parameter.KEYWORD_ONLY:
            kwargs[param_name] = arguments.pop(param_name)
        elif param_kind == Parameter.VAR_KEYWORD:
            kwargs.update(arguments.pop(param_name))
        else:
            raise TypeError('Unknown parameter type')

    if arguments:
        raise ValueError('Too many arguments provided')

    return function(*args, **kwargs)


def update_key_if_none(dictionary: tp.Dict, key: tp.Hashable, value) -> tp.Dict:
    """
    This is deprecated. Please use update_key_if_not_none instead!

    .. deprecated:: 2.14.22
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
