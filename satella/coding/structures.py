# coding=UTF-8
from __future__ import print_function, absolute_import, division
import six
import logging
import copy
import heapq
import functools
from .typecheck import typed, Callable, Iterable


logger = logging.getLogger(__name__)

__all__ = [
    'CallableGroup',
    'Heap',
    'TimeBasedHeap'
]


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


def _extras_to_one(fun):
    @functools.wraps(fun)
    def inner(self, a, *args):
        return fun(self, ((a, ) + args) if len(args) > 0 else a)
    return inner


class Heap(object):
    """
    Sane heap as object - not like heapq.

    Goes from lowest-to-highest (first popped is smallest).
    Standard Python comparision rules apply.

    Not thread-safe
    """

    __slots__ = ('heap', )      # this is rather private, plz

    # TODO needs tests
    @typed(object, (None, Iterable))
    def __init__(self, from_list=None):
        
        if from_list is None:
            self.heap = []
        else:
            self.heap = heapq.heapify(list(from_list))

    @typed(object, Iterable)
    def push_many(self, items):
        for item in items:
            self.push(item)

    # TODO needs tests
    @_extras_to_one
    def push(self, item):
        """
        Use it like:

            heap.push(3)

        or:

            heap.push(4, myobject)
                    """
        heapq.heappush(self.heap, item)

    # TODO needs tests
    def __deepcopy__(self):
        h = Heap()
        h.heap = copy.deepcopy(self.heap)
        return h

    # TODO needs tests
    def __copy__(self):
        h = Heap()
        h.heap = copy.copy(self.heap)
        return h

    # TODO needs tests
    def pop(self):
        """
        :raises IndexError: on empty heap
        """
        return heapq.heappop(self.heap)

    # TODO needs tests
    @typed(object, Callable, Callable)
    def filtermap(self, filterer=lambda i: True, mapfun=lambda i: i):
        """
        Get only items that return True when condition(item) is True. Apply a transform: item' = item(condition) on
        the rest. Maintain heap invariant.
        """
        self.heap = [mapfun(s) for s in self.heap if filterer(s)]
        heapq.heapify(self.heap)

    @typed(returns=bool)
    def __bool__(self):
        """
        Is this empty?
        """
        return len(self.heap) > 0

    @typed(returns=Iterable)
    def iter_ascending(self):
        """
        Return an iterator returning all elements in this heap sorted ascending.
        State of the heap is not changed
        :return: Iterator
        """
        cph = self.copy()
        while cph:
            yield cph.pop()

    @typed(object, object, returns=Iterable)
    def get_less_than(self, less):
        """
        Return all elements less (sharp inequality) than particular value.

        This changes state of the heap
        :param less: value to compare against
        :return: Iterator
        """
        while self:
            if self.heap[0] < less:
                return
            yield self.pop()

    @typed(returns=Iterable)
    def iter_descending(self):
        """
        Return an iterator returning all elements in this heap sorted descending.
        State of the heap is not changed
        :return: Iterator
        """
        return reversed(self.iter_ascending())

    @typed(returns=six.integer_types)
    def __len__(self):
        return len(self)

    def __str__(self):
        return '<satella.coding.Heap: %s elements>' % (len(self.heap, ))

    def __unicode__(self):
        return six.text_type(str(self))

    def __repr__(self):
        return u'<satella.coding.Heap>'

    def __contains__(self, item):
        return item in self.heap

class TimeBasedHeap(Heap):
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
        super(TimeBasedHeap, self).__init__()

    @typed(None, (float, int), None)
    def put(self, timestamp, item):
        """
        Put an item of heap
        :param timestamp: timestamp for this item
        :param item: object
        """
        self.push(timestamp, item)

    @typed(None, (float, int))
    def pop_less_than(self, timestamp):
        """
        Return a list of items with timestamps less than your value.

        Items will be removed from heap
        :return: list of tuple(timestamp::float, item)
        """
        return list(self.get_less_than(timestamp))

    def remove(self, item):
        """
        Remove all things equal to item
        """
        self.filter(lambda i: i != item)

