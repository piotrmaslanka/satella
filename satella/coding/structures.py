# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging
import heapq
from .typecheck import typed, Callable


logger = logging.getLogger(__name__)




class CallableGroup(object):
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
    # todo not threadsafe with oneshots

    def __init__(self, gather=False, swallow_exceptions=False):
        """
        :param gather: if True, results from all callables will be gathered
                       into a list and returned from __call__
        :param swallow_exceptions: if True, exceptions from callables will be
                                   silently ignored. If gather is set,
                                   result will be the exception instance
        """
        self.callables = [] # tuple of (callable, oneshot)
        self.gather = gather
        self.swallow_exceptions = swallow_exceptions

    @typed(None, Callable, bool)
    def add(self, callable, oneshot=False):
        """
        :param oneshot: if True, callable will be unregistered after single call
        """
        self.callables.append((callable, oneshot))

    def __call__(self, *args, **kwargs):
        """
        Run the callable. All registered callables will be called with
        passed arguments, so they should have the same arity.

        If callables raise, it will be passed through.

        :return: list of results if gather was set, else None
        """
        clbl = self.callables       # for moar thread safety
        self.callables = []

        if self.gather:
            results = []

        for callable, oneshot in clbl:
            try:
                q = callable(*args, **kwargs)
            except Exception as e:
                if not self.swallow_exceptions:
                    raise   # re-raise
                q = e

            if self.gather:
                results.append(q)

            if not oneshot:
                self.callables.append((callable, oneshot))

        if self.gather:
            return results


class TimeBasedHeap(object):
    """
    A heap of items sorted by timestamps.

    It is easy to ask for items, whose timestamps are LOWER than a value, and easy
    to remove them.

    Can be used to implement a scheduling service, ie. store jobs, and each interval query
    which of them should be executed. This loses time resolution, but is fast.

    #notthreadsafe
    """

    def __init__(self):
        """
        Initialize an empty heap
        """
        self.heap = []

    def put(self, timestamp, item):
        """
        Put an item of heap
        :param timestamp: timestamp for this item - float
        :param item: object
        """
        heapq.heappush(self.heap, (timestamp, item))

    def pop_less_than(self, timestamp):
        """
        Return a list of items with timestamps less than your value.

        Items will be removed from heap
        :return: list of tuple(timestamp::float, item)
        """
        out = []
        while len(self.heap) > 0:
            if self.heap[0][0] >= timestamp:
                return out
            out.append(heapq.heappop(self.heap))
        return out

    def remove(self, item):
        """
        Remove all things equal to item
        """
        self.heap = [q for q in self.heap if q != item]
        heapq.heapify(self.heap)

