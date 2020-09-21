import queue
import typing as tp
import warnings

from satella.exceptions import PreconditionError

T = tp.TypeVar('T')
U = tp.TypeVar('U')
Expression = tp.NewType('Expression', str)
ExcType = tp.Type[Exception]


# noinspection PyPep8Naming
def _TRUE(x):
    return True


# taken from https://stackoverflow.com/questions/1288498/using-the-same-decorator-with-arguments-wi\
# th-functions-and-methods
def chain_functions(fun_first: tp.Callable[..., tp.Union[tp.Tuple[tp.Tuple, tp.Dict],
                                                         tp.Dict, tp.Tuple]]) -> tp.Callable:
    """
    A decorator to chain function calls.
    This function is expected to return:

     * a 2-tuple [tp.Tuple, tp.Dict] - args and kwargs for the next function
     * tp.Dict - only kwargs will be passed
     * any other tuple - only args will be passed
     * any other type - will be passed as a first argument

    of arguments to pass to wrapped function. So this

    >>> def test3(...):
    >>>     ...
    >>> def test2(...):
    >>>     ...
    >>> def test(...):
    >>>     args, kwargs = test2(...)
    >>>     return test(3)
    >>> v = test(a, b, c)

    Is equivalent to this:
    >>> @chain_functions
    >>> def test2(...):
    >>>     ...
    >>> @test2
    >>> def test3(...):
    >>>     ...
    >>> v = test3(a, b, c)
    """

    def outer(fun_next):
        @wraps(fun_next)
        def inner(*args, **kwargs):
            ret = fun_first(*args, **kwargs)
            if isinstance(ret, dict):
                args = ()
                kwargs = ret
            elif isinstance(ret, tuple) and len(ret) == 2:
                args, kwargs = ret
            elif isinstance(ret, tuple):
                args = ret
                kwargs = {}
            else:
                args = ret,
                kwargs = {}
            return fun_next(*args, **kwargs)

        return inner

    return outer


def wraps(cls_to_wrap: tp.Type) -> tp.Callable[[tp.Type], tp.Type]:
    """
    A functools.wraps() but for classes.

    As a matter of fact, this can replace functools.wraps() entirely.
    This replaces __doc__, __name__, __module__ and __annotations__.
    It also sets a correct __wrapped__.

    :param cls_to_wrap: class to wrap
    """

    def outer(cls: tp.Type) -> tp.Type:
        if hasattr(cls_to_wrap, '__doc__'):
            cls.__doc__ = cls_to_wrap.__doc__
        if hasattr(cls_to_wrap, '__name__'):
            cls.__name__ = cls_to_wrap.__name__
        if hasattr(cls_to_wrap, '__module__'):
            cls.__module__ = cls_to_wrap.__module__
        if hasattr(cls_to_wrap, '__annotations__'):
            cls.__annotations__ = cls_to_wrap.__annotations__
        return cls

    return outer


def has_keys(keys: tp.List[str]):
    """
    A decorator for asserting that a dictionary has given keys. Will raise PreconditionError if
    it doesn't.

    This outputs a callable that accepts a dict and returns True if it has all the keys
    necessary.

    Returns True if the dict has all necessary keys.

    This is meant to be used in conjunction with @precondition

    :param keys: list of keys to expect
    """
    warnings.warn('This is deprecated and will be removed in Satella 3.0. '
                  'Use satella.coding.predicates.has_keys instead', DeprecationWarning)

    def inner(dictionary: dict) -> bool:
        for key in keys:
            if key not in dictionary:
                raise PreconditionError('Key %s not found in dict' % (key,))
        return True

    return inner


def short_none(clb: tp.Union[Expression, tp.Callable[[T], U]]) -> tp.Callable[
        [tp.Optional[T]], tp.Optional[U]]:
    """
    Accept a callable. Return a callable that executes it only if passed a no-None arg,
    and returns its result. If passed a None, return a None

    callable can also be a string, in this case it will be appended to lambda x: and eval'd

    :param clb: callable/1->1
    :return: a modified callable
    """
    if isinstance(clb, str):
        q = dict(globals())
        exec('_callable = lambda x: ' + clb, q)
        clb = q['_callable']

    @wraps(clb)
    def inner(arg: tp.Optional[T]) -> tp.Optional[U]:
        if arg is None:
            return None
        else:
            return clb(arg)

    return inner
