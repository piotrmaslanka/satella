import itertools
import typing as tp

from satella.exceptions import PreconditionError
from .decorators import wraps

T = tp.TypeVar('T')
Expression = tp.NewType('Expression', str)
Condition = tp.Union[tp.Callable[[T], bool], Expression]

# noinspection PyPep8Naming
def _TRUE(x):
    return True


def precondition(*t_ops: Condition, **kw_opts: Condition):
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
    only if they are passed, so make your default arguments obey the precondition, because
    it won't
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
                        raise PreconditionError('Argument %s failed precondition check' %
                                                (kwarg,))

            with rethrow_as(TypeError, PreconditionError):
                for arg, precond in itertools.zip_longest(args, tn_ops, fillvalue=_TRUE):
                    if precond(arg) is False:
                        raise PreconditionError(
                            'Argument of value %s failed precondition check' % (arg,))
            return fun(*args, **kwargs)

        return inner

    return outer


def postcondition(condition: Condition):
    """
    Return a decorator, asserting that result of this function, called with provided
    callable,
    is True, else the function will raise PreconditionError.

    :param condition: callable that accepts a single argument, the return value of the function.
        Can be also a string, in which case it is an expression about the value x of return
    """
    if isinstance(condition, str):
        q = dict(globals())
        exec('_precond = lambda x: ' + condition, q)
        condition = q['_precond']

    def outer(fun):
        @wraps(fun)
        def inner(*args, **kwargs):
            v = fun(*args, **kwargs)
            if condition(v) is False:
                raise PreconditionError('Condition not true')
            return v

        return inner

    return outer
