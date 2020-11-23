import threading
import typing as tp
import warnings
from concurrent.futures import Executor

from satella.coding.decorators.decorators import wraps
from satella.warnings import ExperimentalWarning

local_ee = threading.local()

__all__ = ['Call', 'CallIf', 'CallWithArgumentSet', 'ExecutionEnvironment', 'call_with_ee',
           'package_for_execution', 'current_call', 'current_args', 'current_history',
           'current_kwargs', 'current_ee']


def push_call_stack(cs: tp.Callable, args: tuple = (), kwargs: tp.Optional[dict] = None) -> None:
    kwargs = kwargs or {}
    arg_tuple = ((cs, args, kwargs), )
    if not hasattr(local_ee, 'cs'):
        local_ee.cs = arg_tuple
    else:
        local_ee.cs = local_ee.cs + arg_tuple


def pop_call_stack() -> tp.Optional[tp.Tuple[tp.Callable, tuple, dict]]:
    if not hasattr(local_ee, 'cs'):
        return None
    cs = local_ee.cs
    if not cs:
        return None
    v = cs[-1]
    local_ee.cs = local_ee.cs[:-1]
    return v


def before_call(fun):
    @wraps(fun)
    def inner(self, *args, **kwargs):
        if not hasattr(local_ee, 'ee'):
            v = call_with_ee(fun, ExecutionEnvironment([(args, kwargs)]))
            return v(self, *args, **kwargs)
        else:
            return fun(self, *args, **kwargs)

    return inner


class Call:
    """
    A call to given function with a given set of arguments
    """
    __slots__ = ('fn', 'args', 'kwargs')

    def __init__(self, fn, *args, **kwargs):
        warnings.warn('This module is experimental, use at your own peril', ExperimentalWarning)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @before_call
    def __call__(self, *args, **kwargs):
        """
        Call this callable.

        If an execution environment is already defined, it will be used. If not,
        a new execution environment will be defined with the 0-th set of arguments
        as args, kwargs.

        :param args: args to use as the 0-th set of arguments
        :param kwargs: kwargs to use as the 0-th set of arguments
        :return: return value
        """
        push_call_stack(self, self.args, self.kwargs)
        try:
            return self.fn(*self.args, **self.kwargs)
        finally:
            pop_call_stack()


class CallWithArgumentSet(Call):
    """
    Call a function with a set of arguments provided by the environment
    """
    __slots__ = ('fn', 'arg_set_no')

    def __init__(self, fn, arg_set_no: int = 0):
        warnings.warn('This module is experimental, use at your own peril', ExperimentalWarning)
        self.fn = fn
        self.arg_set_no = arg_set_no

    @before_call
    def __call__(self, *args, **kwargs):
        try:
            ee = local_ee.ee
        except AttributeError:
            raise RuntimeError('Execution environment is required!')
        args, kwargs = ee[self.arg_set_no]
        push_call_stack(self, args, kwargs)
        try:
            return self.fn(*args, **kwargs)
        finally:
            pop_call_stack()


class CallIf(Call):
    """
    Call a function only if fn_if_call returned True
    """
    __slots__ = ('fn_to_call', 'fn_call_if')

    def __init__(self, fn_if_call: Call, fn_to_call: Call):
        warnings.warn('This module is experimental, use at your own peril', ExperimentalWarning)
        self.fn_to_call = fn_to_call
        self.fn_call_if = fn_if_call

    @before_call
    def __call__(self, *args, **kwargs):
        if self.fn_call_if():
            return self.fn_to_call()


class Reduce(Call):
    """
    A call consisting of calling other calls (possibly in parallel).

    It's result will be the combination of some other function calls by a given operator,
    starting with a starting value.

    By default the starting operator just discards the results.

    :param callables: callables to call in parallel
    :param reducing_op: a callable/2 that takes previous result (or the starting value) and current
        callable result, returning a new starting value
    :param starting_value: starting value
    :param do_parallel: whether try to execute these calls in parallel, if possible.
        Parallel execution will be done only if an executor is given in the execution environment.
    """
    __slots__ = ('reducing_op', 'starting_value', 'do_parallel', 'callables')

    def __init__(self, *callables: Call,
                 reducing_op: tp.Callable[[tp.Any, tp.Any], tp.Any] = lambda a, b: None,
                 starting_value: tp.Any = 0,
                 do_parallel: bool = True):
        warnings.warn('This module is experimental, use at your own peril', ExperimentalWarning)
        self.reducing_op = reducing_op
        self.starting_value = starting_value
        self.do_parallel = do_parallel
        self.callables = callables

    @before_call
    def __call__(self, *args, **kwargs):
        push_call_stack(self)
        if self.do_parallel:
            if local_ee.ee.executor is not None:
                executor = local_ee.ee.executor
                sv = self.starting_value
                futures = [executor.submit(call_with_ee(callable_, local_ee.ee, local_ee.cs))
                           for callable_ in self.callables]
                for future in futures:
                    sv = self.reducing_op(sv, future.result())
                return sv
        sv = self.starting_value
        for callable_ in self.callables:
            b = callable_()
            sv = self.reducing_op(sv, b)
        pop_call_stack()
        return sv


class ExecutionEnvironment:
    """
    This has no __slots__ so you can add anything here really
    """

    def __init__(self, argument_sets: tp.Iterable[tp.Tuple[tp.Tuple[tp.Any], tp.Dict]],
                 executor: tp.Optional[Executor] = None,
                 cs=()):
        self.arg_sets = []
        for args, kwargs in argument_sets:
            self.arg_sets.append((args, kwargs))
        self.executor = executor
        self.cs = cs

    def _set_call_stack_to(self, cs: tp.Optional[tp.List[tp.Callable]] = None):
        return ExecutionEnvironment(self.arg_sets, self.executor, cs)

    def __call__(self, callable_: Call, *args, **kwargs):
        """
        Run a given callable within the current EE.

        :param callable_: callable to run
        :return: value returned by that callable
        """
        had_cs = hasattr(local_ee, 'cs')
        if had_cs:
            prev_cs = local_ee.cs

        local_ee.cs = self.cs

        had_ee = hasattr(local_ee, 'ee')
        if had_ee:
            prev_ee = local_ee.ee
        local_ee.ee = self
        try:
            return callable_(*args, **kwargs)
        finally:
            if had_ee:
                local_ee.ee = prev_ee
            else:
                del local_ee.ee
            if had_cs:
                local_ee.cs = prev_cs
            else:
                del local_ee.cs

    def __getitem__(self, item: int) -> tp.Tuple[tp.Tuple, tp.Dict]:
        """Return the n-th argument set"""
        try:
            v = self.arg_sets[item]
        except IndexError:
            v = (), {}
        return v


def call_with_ee(callable_: tp.Callable, ee: ExecutionEnvironment,
                 _copy_call_stack_from: tp.Optional[tp.List[tp.Callable]] = None) -> tp.Callable:
    """
    Return a callable that will invoke the target callable with specified execution environment,
    but only if an EE is not defined right now.

    To explicitly provide an execution environment use this:

    >>> call_1 = Call(...)
    >>> ee = ExecutionEnvironment()
    >>> ee(call_1)

    :param callable_: callable to invoke
    :param ee: execution environment to use
    :param _copy_call_stack_from: used internally, don't use
    :return: a new callable
    """
    warnings.warn('This module is experimental, use at your own peril', ExperimentalWarning)

    def inner(*args, **kwargs):
        if not hasattr(local_ee, 'ee'):
            if _copy_call_stack_from is not None:
                ef = ee._set_call_stack_to(_copy_call_stack_from)
            else:
                ef = ee
            return ef(callable_, *args, **kwargs)
        else:
            return callable_(*args, **kwargs)

    return inner


def package_for_execution(clbl: tp.Callable, ee: ExecutionEnvironment) -> tp.Callable:
    """
    Return a callable that, when called, will call specified callable in target
    execution environment.

    :param clbl: callable to run
    :param ee: EE to use
    :return: a callable
    """
    warnings.warn('This module is experimental, use at your own peril', ExperimentalWarning)

    def inner():
        return ee(clbl)

    return inner


def call(fun):
    """
    Make the decorated function a callable, with it's args and kwargs to be set as a 0-th argument
    set.
    """
    a = CallWithArgumentSet(fun, 0)
    return wraps(fun)(a)


def current_ee() -> ExecutionEnvironment:
    warnings.warn('This module is experimental, use at your own peril', ExperimentalWarning)
    return local_ee.ee


def current_call() -> Call:
    """
    Return currently processed Call, or None if not available
    """
    warnings.warn('This module is experimental, use at your own peril', ExperimentalWarning)
    return local_ee.cs[-1][0]


def current_args() -> tp.Optional[tuple]:
    """
    Return currently used positional arguments, or None if not available
    """
    warnings.warn('This module is experimental, use at your own peril', ExperimentalWarning)
    if not local_ee.cs:
        return None
    return local_ee.cs[-1][1]


def current_kwargs() -> tp.Optional[dict]:
    """
    Return currently used kwargs, or None if not available
    """
    warnings.warn('This module is experimental, use at your own peril', ExperimentalWarning)
    if not local_ee.cs:
        return None
    return local_ee.cs[-1][2]


def current_history() -> tp.Tuple[tp.Tuple[Call, tuple, dict]]:
    """
    Return a tuple of subsequent calls that led to this call.

    Position 0 will have the absolutely first call in the hierarchy, where -1 will have the current
    one.
    :return: a tuple of tuples (Call instance, args tuple, kwargs dict)
    """
    warnings.warn('This module is experimental, use at your own peril', ExperimentalWarning)
    return local_ee.cs
