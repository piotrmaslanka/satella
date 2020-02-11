import functools
import typing as tp
import itertools

from ..exceptions import PreconditionError

__all__ = ['precondition', 'for_argument', 'PreconditionError', 'short_none']

_NOP = lambda x: x
_TRUE = lambda x: True


def short_none(callable_: tp.Union[str, tp.Callable[[tp.Any], tp.Any]]) -> tp.Callable[[tp.Any], tp.Any]:
    """
    Accept a callable. Return a callable that executes it only if passed a no-None arg, and returns
    its result.
    If passed a None, return a None

    callable can also be a string, in this case it will be appended to lambda x: and eval'd

    :param callable_: callable/1->1
    :return: a modified callable
    """
    if isinstance(callable_, str):
        q = dict(globals())
        exec('_precond = lambda x: '+callable_, q)
        callable_ = q['_precond']

    @functools.wraps(callable_)
    def inner(arg):
        if arg is None:
            return None
        else:
            return callable_(arg)
    return inner


def precondition(*t_ops, **kw_opts):
    """
    Check that a precondition happens for given parameter.
    Only positional arguments are supported.

    You can do it like this:

    >>> @precondition(lambda x: x == 1)
    >>> def return_two(x):
    >>>     return x*2

    or

    >>> @precondition('x == 1')
    >>> def return_two(x):
    >>>     ..

    If None is passed then argument will be always assumed to be True.
    You can use all standard locals in precondition.

    You function call will return a PreconditionError (subclass of
    ValueError) if a precondition fails.

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
            exec('_precond = lambda x: '+value, q)
            precond_ = q['_precond']
        else:
            precond_ = value
        kw_ops[kwarg_] = precond_

    from satella.coding.recast_exceptions import rethrow_as

    def outer(fun):
        @functools.wraps(fun)
        def inner(*args, **kwargs):
            assert len(args) >= len(tn_ops), 'More preconditions than positional arguments!'

            for kwarg in kwargs:
                if kwarg in kw_ops:
                    if not kw_ops[kwarg](kwargs[kwarg]):
                        raise PreconditionError('Argument %s failed precondition check' % (kwarg, ))

            with rethrow_as(TypeError, PreconditionError):
                for arg, precond in itertools.zip_longest(args, tn_ops, fillvalue=_TRUE):
                    if not precond(arg):
                        raise PreconditionError(
                            'Argument of value %s failed precondition check' % (arg,))
            return fun(*args, **kwargs)

        return inner

    return outer


def for_argument(*t_ops, **t_kwops):
    """
    Calls a callable for each of the arguments. Pass None if you do not wish to process given argument.

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
        @functools.wraps(fun)
        def inner(*args, **kwargs):
            # add extra 'None' argument if unbound method
            assert len(args) >= len(t_ops)
            a = fun(*((_NOP if op is None else op)(arg) for arg, op in
                      itertools.zip_longest(args, t_ops, fillvalue=None)),
                    **{k: t_kwops.get(k, _NOP)(v) for k, v in kwargs.items()})
            return returns(a)

        return inner

    return outer
