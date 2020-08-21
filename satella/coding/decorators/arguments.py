import itertools
import typing as tp

from .decorators import wraps
from ..misc import source_to_function

T = tp.TypeVar('T')
U = tp.TypeVar('U')


# noinspection PyPep8Naming
def _NOP(x):
    return x


def execute_before(callable_: tp.Callable) -> tp.Callable:
    """
    Wrapper to create wrappers which execute callable before function launch.

    Use like this:

    >>> @execute_before
    >>> def do_things():
    >>>     print('Things are done')

    Then the following will print 'Things are done'
    >>> @do_things
    >>> def nothing():
    >>>     ...
    >>> nothing()

    You can even specify custom parameters for the callable:

    >>> @execute_before
    >>> def i_am_2(two):
    >>>     assert two == 2
    >>> @i_am_2(2)
    >>> def run_me():
    >>>     pass
    """

    def outer(*args, **kwargs):
        if len(args) == 1 and not kwargs and callable(args[0]):
            @wraps(args[0])
            def inner(*my_args, **my_kwargs):
                callable_()
                return args[0](*my_args, **my_kwargs)

            return inner
        else:
            def inner(func):
                @wraps(func)
                def inner2(*my_args, **my_kwargs):
                    callable_(*args, **kwargs)
                    return func(*my_args, **my_kwargs)
                return inner2
            return inner

    return outer


def auto_adapt_to_methods(decorator):
    """
    Allows you to use the same decorator on methods and functions,
    hiding the self argument from the decorator.

    Usage:

    >>> @auto_adapt_to_methods
    >>> def times_two(fun):
    >>>     def outer(a):
    >>>         return fun(a*2)
    >>>     return outer
    >>> class Test:
    >>>     @times_two
    >>>     def twice(self, a):
    >>>         return a*2
    >>> @times_two
    >>> def twice(a):
    >>>     return a*2
    >>> assert Test().twice(2) == 4
    >>> assert twice(2) == 4
    """

    def adapt(func):
        return _MethodDecoratorAdaptor(decorator, func)

    return adapt


class _MethodDecoratorAdaptor:
    __slots__ = ('decorator', 'func')

    def __init__(self, decorator, func):
        self.decorator = decorator
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.decorator(self.func)(*args, **kwargs)

    def __get__(self, instance, owner):
        return self.decorator(self.func.__get__(instance, owner))


def attach_arguments(*args, **kwargs):
    """
    Return a decorator that passes extra arguments to the function.

    Example:

    >>> @attach_arguments(2, label='value')
    >>> def print_args(*args, **kwargs):
    >>>     print(args, kwargs)
    >>> print_args(3, 4, key='value')

    will print

    >>> (3, 4, 2) {'key': 'value', 'label': 'value'}

    Arguments given in attach_arguments will take precedence in case of key collisions.
    """

    def outer(fun):
        @wraps(fun)
        def inner(*my_args, **my_kwargs):
            my_kwargs.update(kwargs)
            return fun(*my_args, *args, **my_kwargs)

        return inner

    return outer


ForArgumentArg = tp.Union[tp.Callable[[T], U], str]


def for_argument(*t_ops: ForArgumentArg, **t_kwops: ForArgumentArg):
    """
    Calls a callable for each of the arguments. Pass None if you do not wish to process given
    argument.

    returns is a special keyword, a callable to process the result through

    Use like:

    >>> @for_argument(int, str, typed=bool, returns=int)
    >>> def check(val1, val2, typed='True'):
    >>>     if typed:
    >>>         return val1 + int(val2)

    for_argument can also accept strings as expressions:

    >>> @for_argument('x*2')
    >>> def accept_two(x):
    >>>     assert x == 2
    >>> accept_two(1)
    """
    new_t_ops = []
    for op in t_ops:
        if op == 'self':
            new_t_ops.append(_NOP)
        elif op is None:
            new_t_ops.append(_NOP)
        elif isinstance(op, str):
            new_t_ops.append(source_to_function(op))
        else:
            new_t_ops.append(op)

    t_ops = new_t_ops
    returns = t_kwops.pop('returns', _NOP)

    for key, value in t_kwops.items():
        if value is None:
            t_kwops[key] = _NOP
        elif isinstance(value, str):
            t_kwops[key] = source_to_function(value)

    def outer(fun):
        @wraps(fun)
        def inner(*args, **kwargs):
            # add extra 'None' argument if unbound method
            assert len(args) >= len(t_ops)
            a = fun(*((_NOP if op is None else op)(arg) for arg, op in
                      itertools.zip_longest(args, t_ops, fillvalue=None)),
                    **{k: t_kwops.get(k, _NOP)(v) for k, v in kwargs.items()})
            return returns(a)

        return inner

    return outer
