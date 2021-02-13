import copy
import inspect
import itertools
import typing as tp
from inspect import Parameter

from satella.coding.typing import T, Predicate
from .decorators import wraps
from ..misc import source_to_function, get_arguments, call_with_arguments, _get_arguments
from ..predicates import PredicateClass, build_structure

U = tp.TypeVar('U')


# noinspection PyPep8Naming
def _NOP(x):
    return x


def transform_result(expr: str):
    """
    A decorator transforming the result value of a function by a Python expression.

    The result is feeded as the local variable "x", while arguments are fed as if they were
    expressed as arguments, eg:

    >>> @transform_result('x*a')
    >>> def square(a):
    >>>     return a

    :param expr: Python string expression
    """
    def outer(fun):
        @wraps(fun)
        def inner(*args, **kwargs):
            a = fun(*args, **kwargs)
            local = get_arguments(fun, *args, *kwargs)
            local['x'] = a
            return eval(expr, globals(), local)
        return inner
    return outer


def transform_arguments(**expressions: str):
    """
    A decorator transforming the arguments of a function prior to it's execution.

    The arguments are always bound as if they were available in the function.

    The expressions always operate on "old" arguments

    >>> @transform_arguments(a='a*a')
    >>> def square(a):
    >>>     return a

    :param expressions: Python strings that are meant to be evaluated
    """
    def outer(fun):
        @wraps(fun)
        def inner(*args, **kwargs):
            old_args = get_arguments(fun, *args, *kwargs)
            new_args = {}
            for arg, arg_value in expressions.items():
                new_args[arg] = eval(arg_value, globals(), old_args)
            for new_arg in old_args:
                if new_arg not in new_args:
                    new_args[new_arg] = old_args[new_arg]
            return call_with_arguments(fun, new_args)
        return inner
    return outer


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


def replace_argument_if(arg_name: str,
                        structure: tp.Union[dict, list, tuple, PredicateClass],
                        instance_of: tp.Optional[tp.Union[tp.Type, tp.Tuple[tp.Type, ...]]] = None,
                        predicate: tp.Optional[Predicate] = None,
                        ):
    """
    Examine arguments of the callable that will be decorated with this.

    If argument arg_name is found to be an instance of instance_of, it will be replaced
    by a structure defined a structure.

    :param arg_name: argument to replace
    :param instance_of: type
    :param predicate: alternative condition of replacement. If this is given,
        predicate is called on the value of the argument and replacement is done
        if it returns True
    :param structure: a callable that takes original argument and returns new, or a
        structure made of these
    """

    def outer(fun):
        @wraps(fun)
        def inner(*args, **kwargs):
            args_dict = get_arguments(fun, *args, **kwargs)
            altered = False
            if arg_name in args_dict:
                v = args_dict[arg_name]
                if predicate is not None:
                    args_dict[arg_name] = build_structure(structure, v)
                    altered = True
                elif isinstance(v, instance_of):
                    args_dict[arg_name] = build_structure(structure, v)
                    altered = True
            if altered:
                return call_with_arguments(fun, args_dict)
            else:
                return fun(*args, **kwargs)

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


def copy_arguments(deep_copy: bool = False) -> tp.Callable:
    """
    Make every argument passe to this function be copied.

    This way you can pass dictionaries to the function that would normally have modified them.

    Use like this:

    >>> @copy_arguments()
    >>> def alter_dict(dct: dict)
    >>>     return dct.pop('a')

    Now you can use it like this:

    >>> b = {'a': 5}
    >>> assert alter_dict(b) == 5
    >>> assert b == {'a': 5}

    :param deep_copy: whether to use deepcopy instead of a plain copy
    """
    f_copy = copy.deepcopy if deep_copy else copy.copy

    def outer(fun):
        @wraps(fun)
        def inner(*args, **kwargs):
            args = tuple(f_copy(arg) for arg in args)
            kwargs = {name: f_copy(value) for name, value in kwargs.items()}
            return fun(*args, **kwargs)

        return inner

    return outer


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

    for_argument will also recognize default values:

    >>> @for_argument(k=int)
    >>> def for_arg(k='5')
    >>>     print(repr(k))
    >>> for_arg()
    will print `5` instead of `'5'`.

    Note that for_argument is quite slow when it comes to having default values
    in the function signature. Best to avoid it if you need speed.

    If it detects that the function that you passed does not use default values,
    it will use the faster implementation.
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
        comparison = False
        # Check whether this function has any default arguments
        for param in inspect.signature(fun).parameters.values():
            try:
                if Parameter.empty != param.default:
                    comparison = True
                    break
            except (AttributeError, TypeError):
                comparison = True
                break

        if comparison:
            @wraps(fun)
            def inner(*args, **kwargs):
                dict_operations = _get_arguments(fun, True, *t_ops, **t_kwops)
                dict_values = get_arguments(fun, *args, **kwargs)
                arguments = {}
                for arg_name in dict_values:
                    v = dict_values[arg_name]
                    if arg_name in dict_operations:
                        f = dict_operations[arg_name]
                        if callable(f) and f is not None:
                            v = f(v)

                    arguments[arg_name] = v

                return returns(call_with_arguments(fun, arguments))
        else:
            @wraps(fun)
            def inner(*args, **kwargs):
                # add extra 'None' argument if unbound method
                assert len(args) >= len(t_ops)
                a = fun(*((_NOP if op2 is None else op2)(arg) for arg, op2 in
                          itertools.zip_longest(args, t_ops, fillvalue=None)),
                        **{k: t_kwops.get(k, _NOP)(v) for k, v in kwargs.items()})
                return returns(a)

        return inner

    return outer
