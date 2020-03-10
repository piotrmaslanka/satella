import logging
import collections
import copy
import typing as tp

logger = logging.getLogger(__name__)

__all__ = [
    'CallableGroup',
]


class CallableGroup:
    """
    This behaves like a function, but allows to add other functions to call
    when invoked, eg.

        c1 = Callable()

        c1.add(foo)
        c1.add(bar)

        c1(2, 3)

    Now both foo and bar will be called with arguments (2, 3). Their exceptions
    will be propagated.

    """

    def __init__(self, gather: bool = True, swallow_exceptions: bool = False):
        """
        :param gather: if True, results from all callables will be gathered
                       into a list and returned from __call__
        :param swallow_exceptions: if True, exceptions from callables will be
                                   silently ignored. If gather is set,
                                   result will be the exception instance
        """
        self.callables = collections.OrderedDict()  # type: tp.Dict[tp.Callable, bool]
        self.gather = gather    # type: bool
        self.swallow_exceptions = swallow_exceptions    # type: bool

    def add(self, callable_: tp.Callable, one_shot: bool = False):
        """
        :param callable_: callable
        :param one_shot: if True, callable will be unregistered after single call
        """
        from ..structures.hashable_objects import HashableWrapper
        callable_ = HashableWrapper(callable_)
        if callable_ in self.callables:
            return
        self.callables[callable_] = one_shot

    def __call__(self, *args, **kwargs):
        """
        Run the callable. All registered callables will be called with
        passed arguments, so they should have the same arity.

        If callables raise, it will be passed through.

        :return: list of results if gather was set, else None
        """
        callables = copy.copy(self.callables)

        results = []

        for call, one_shot in callables.items():
            try:
                q = call(*args, **kwargs)
            except Exception as e:
                if not self.swallow_exceptions:
                    raise  # re-raise
                q = e

            if self.gather:
                results.append(q)

            if not one_shot:
                self.add(call, one_shot)

        if self.gather:
            return results
