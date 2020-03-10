import itertools
import typing as tp

from ..exceptions import PreconditionError

__all__ = ['precondition', 'for_argument', 'PreconditionError', 'short_none', 'has_keys',
           'attach_arguments', 'wraps']

T = tp.TypeVar('T')
U = tp.TypeVar('U')
Expression = tp.NewType('Expression', str)


def _NOP(x):
    return x


def _TRUE(x):
    return True


def wraps(cls_to_wrap: tp.Type) -> tp.Callable[[tp.Type], tp.Type]:
    """
    A functools.wraps() but for classes.

    As a matter of fact, this can replace functools.wraps() entirely.

    :param cls_to_wrap: class to wrap
    """

    def outer(cls: tp.Type) -> tp.Type:
        if hasattr(cls_to_wrap, '__doc__'):
            cls.__doc__ = cls_to_wrap.__doc__
        if hasattr(cls_to_wrap, '__name__'):
            cls.__name__ = cls_to_wrap.__name__
        if hasattr(cls_to_wrap, '__module__'):
            cls.__module__ = cls_to_wrap.__module__
        return cls

    return outer


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


def has_keys(keys: tp.List[str]):
    """
    A decorator for asserting that a dictionary has given keys. Will raise PreconditionError if
    it doesn't.

    This outputs a callable that accepts a dict and returns True if it has all the keys necessary.

    Returns True if the dict has all necessary keys.

    This is meant to be used in conjunction with @precondition

    :param keys: list of keys to expect
    """

    def inner(dictionary: dict) -> bool:
        for key in keys:
            if key not in dictionary:
                raise PreconditionError('Key %s not found in dict' % (key,))
        return True

    return inner


def short_none(clb: tp.Union[Expression, tp.Callable[[T], U]]) -> tp.Callable[
    [tp.Optional[T]], tp.Optional[U]]:
    """
    Accept a callable. Return a callable that executes it only if passed a no-None arg, and returns
    its result.
    If passed a None, return a None

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


def precondition(*t_ops: tp.Union[tp.Callable[[T], bool], Expression],
                 **kw_opts: tp.Union[tp.Callable[[T], bool], Expression]):
    """
    Check that a precondition happens for given parameter.

    You can do it like this:

    >>> @precondition(lambda x: x == 1)
    >>> def return_two(x):
    >>>     return x*2

    or

    >>> @precondition('x == 1')
    >>> def return_two(x):
    >>>     ..

    You can use all standard locals in precondition.

    You function call will return a PreconditionError (subclass of
    ValueError) if a precondition fails.

    A precondition of None will always be true.

    Keyword arguments are supported as well. Note that precondition for them will be checked
    only if they are passed, so make your default arguments obey the precondition, because it won't
    be checked if the default value is used.
    """

    tn_ops = []

    for t_op in t_ops:
        if t_op is None:
            precond_ = _TRUE
        elif isinstance(t_op, str):
            q = dict(globals())
            exec('_precond = lambda x: ' + t_op, q)
            precond_ = q['_precond']
        else:
            precond_ = t_op

        tn_ops.append(precond_)

    kw_ops = {}
    for kwarg_, value in kw_opts.items():
        if value is None:
            precond_ = _TRUE
        elif isinstance(value, str):
            q = dict(globals())
            exec('_precond = lambda x: ' + value, q)
            precond_ = q['_precond']
        else:
            precond_ = value
        kw_ops[kwarg_] = precond_

    from satella.coding.recast_exceptions import rethrow_as

    def outer(fun):
        @wraps(fun)
        def inner(*args, **kwargs):
            assert len(args) >= len(tn_ops), 'More preconditions than positional arguments!'

            for kwarg in kwargs:
                if kwarg in kw_ops:
                    if not kw_ops[kwarg](kwargs[kwarg]):
                        raise PreconditionError('Argument %s failed precondition check' % (kwarg,))

            with rethrow_as(TypeError, PreconditionError):
                for arg, precond in itertools.zip_longest(args, tn_ops, fillvalue=_TRUE):
                    if not precond(arg):
                        raise PreconditionError(
                            'Argument of value %s failed precondition check' % (arg,))
            return fun(*args, **kwargs)

        return inner

    return outer


def for_argument(*t_ops: tp.Callable[[T], U], **t_kwops: tp.Callable[[T], U]):
    """
    Calls a callable for each of the arguments. Pass None if you do not wish to process given
    argument.

    returns is a special keyword, a callable to process the result through

    Use like:

    >>> @for_argument(int, str, typed=bool, returns=int)
    >>> def check(val1, val2, typed='True'):
    >>>     if typed:
    >>>         return val1 + int(val2)
    """
    t_ops = [_NOP if op == 'self' else op for op in t_ops]
    returns = t_kwops.pop('returns', _NOP)

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
