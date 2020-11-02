import logging
import threading
import typing as tp
from concurrent.futures import Executor

from satella.coding.decorators.decorators import wraps

local_ee = threading.local()
logger = logging.getLogger(__name__)

__all__ = ['Call', 'CallIf', 'CallWithArgumentSet', 'ExecutionEnvironment', 'call_with_ee',
           'package_for_execution']


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

    def __init__(self, fn, *args, **kwargs):
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
        return self.fn(*self.args, **self.kwargs)


class CallWithArgumentSet(Call):
    """
    Call a function with a set of arguments provided by the environment
    """

    def __init__(self, fn, arg_set_no: int = 0):
        self.fn = fn
        self.arg_set_no = arg_set_no

    @before_call
    def __call__(self, *args, **kwargs):
        try:
            ee = local_ee.ee
        except AttributeError:
            raise RuntimeError('Execution environment is required!')
        args, kwargs = ee[self.arg_set_no]
        v = self.fn(*args, **kwargs)
        return v


class CallIf(Call):
    """
    Call a function only if fn_if_call returned True
    """

    def __init__(self, fn_if_call: Call, fn_to_call: Call):
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

    def __init__(self, *callables: Call,
                 reducing_op: tp.Callable[[tp.Any, tp.Any], tp.Any] = lambda a, b: None,
                 starting_value: tp.Any = 0,
                 do_parallel: bool = True):
        self.reducing_op = reducing_op
        self.starting_value = starting_value
        self.do_parallel = do_parallel
        self.callables = callables

    @before_call
    def __call__(self, *args, **kwargs):
        if self.do_parallel:
            if local_ee.ee.executor is not None:
                executor = local_ee.ee.executor
                sv = self.starting_value
                futures = [executor.submit(call_with_ee(callable_, local_ee.ee))
                           for callable_ in self.callables]
                for future in futures:
                    sv = self.reducing_op(sv, future.result())
                return sv
        sv = self.starting_value
        for callable_ in self.callables:
            b = callable_()
            sv = self.reducing_op(sv, b)
        return sv


class ExecutionEnvironment:
    __slots__ = ('arg_sets', 'executor')

    def __init__(self, argument_sets: tp.Iterable[tp.Tuple[tp.Tuple[tp.Any], tp.Dict]],
                 executor: tp.Optional[Executor] = None):
        self.arg_sets = []
        for args, kwargs in argument_sets:
            self.arg_sets.append((args, kwargs))
        self.executor = executor

    def __call__(self, callable_: Call, *args, **kwargs):
        """
        Run a given callable within the current EE.

        :param callable_: callable to run
        :return: value returned by that callable
        """
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

    def __getitem__(self, item: int) -> tp.Tuple[tp.Tuple, tp.Dict]:
        """Return the n-th argument set"""
        v = self.arg_sets[item]
        return v


def call_with_ee(callable_: tp.Callable, ee: ExecutionEnvironment) -> tp.Callable:
    """
    Return a callable that will invoke the target callable with specified execution environment,
    but only if an EE is not defined right now.

    To explicitly provide an execution environment use this:

    >>> call_1 = Call(...)
    >>> ee = ExecutionEnvironment()
    >>> ee(call_1)

    :param callable_: callable to invoke
    :param ee: execution environment to use
    :return: a new callable
    """

    def inner(*args, **kwargs):
        if not hasattr(local_ee, 'ee'):
            return ee(callable_, *args, **kwargs)
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

    def inner():
        return ee(clbl)

    return inner
