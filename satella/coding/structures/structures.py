import copy
import functools
import heapq
import logging
import typing as tp
import operator
import time

logger = logging.getLogger(__name__)

__all__ = [
    'Heap',
    'TimeBasedHeap',
    'OmniHashableMixin'
]


class OmniHashableMixin:
    _HASH_FIELDS_TO_USE = []

    def __hash__(self):
        return functools.reduce(operator.xor, (hash(getattr(self, fname)) \
                                               for fname in self._HASH_FIELDS_TO_USE))

    def __eq__(self, other):
        cons = lambda p: [getattr(p, fname) for fname in self._HASH_FIELDS_TO_USE]
        if cons(self) == cons(other):
            return True

        if not isinstance(other, OmniHashableMixin):
            return str(self) == str(other)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


def _extras_to_one(fun):
    @functools.wraps(fun)
    def inner(self, a, *args, **kwargs):
        return fun(self, ((a,) + args) if len(args) > 0 else a, **kwargs)

    return inner


class Heap(object):
    """
    Sane heap as object - not like heapq.

    Goes from lowest-to-highest (first popped is smallest).
    Standard Python comparision rules apply.

    Not thread-safe
    """

    def __init__(self, from_list=()):
        self.heap = list(from_list)
        heapq.heapify(self.heap)

    def push_many(self, items: tp.Iterable):
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

    def __copie(self, op):
        h = Heap()
        h.heap = op(self.heap)
        return h

    def __deepcopy__(self, memo):
        return self.__copie(copy.deepcopy)

    def __copy__(self):
        return self.__copie(copy.copy)

    def __iter__(self):
        return self.heap.__iter__()

    def pop(self) -> tp.Any:
        """
        Return smallest element of the heap.
        :raises IndexError: on empty heap
        """
        return heapq.heappop(self.heap)

    def filtermap(self, filter_fun: tp.Optional[tp.Callable] = None,
                  map_fun: tp.Optional[tp.Callable] = None):
        """
        Get only items that return True when condition(item) is True. Apply a
         transform: item' = item(condition) on
        the rest. Maintain heap invariant.
        """
        heap = filter(filter_fun, self.heap) if filter_fun else self.heap
        heap = map(map_fun, heap) if map_fun else heap
        heap = list(heap) if not isinstance(heap, list) else heap
        self.heap = heap
        heapq.heapify(self.heap)

    def __bool__(self) -> bool:
        """
        Is this empty?
        """
        return len(self.heap) > 0

    def iter_ascending(self) -> tp.Iterator:
        """
        Return an iterator returning all elements in this heap sorted ascending.
        State of the heap is not changed
        :return: Iterator
        """
        heap = copy.copy(self.heap)
        while heap:
            yield heapq.heappop(heap)

    def iter_descending(self) -> tp.Iterator:
        """
        Return an iterator returning all elements in this heap sorted descending.
        State of the heap is not changed
        :return: Iterator
        """
        return reversed(list(self.iter_ascending()))

    def __len__(self) -> int:
        return len(self.heap)

    def __str__(self):
        return '<satella.coding.Heap: %s elements>' % (len(self, ))

    def __repr__(self):
        return u'<satella.coding.Heap>'

    def __contains__(self, item) -> bool:
        return item in self.heap


class TimeBasedHeap(Heap):
    """
    A heap of items sorted by timestamps.

    It is easy to ask for items, whose timestamps are LOWER than a value, and
    easy to remove them.

    Can be used to implement a scheduling service, ie. store jobs, and each
    interval query
    which of them should be executed. This loses time resolution, but is fast.

    Can use current time with put/pop_less_than.
    Use default_clock_source to pass a callable:

      * time.time

    #notthreadsafe
    """

    def __repr__(self):
        return u'<satella.coding.TimeBasedHeap>'

    def items(self) -> tp.Iterable:
        """
        Return an iterator, but WITHOUT timestamps (only items), in
        unspecified order
        """
        return (ob for ts, ob in self.heap)

    def __init__(self, default_clock_source: tp.Callable[[], int] = None):
        """
        Initialize an empty heap
        """
        self.default_clock_source = default_clock_source or time.time
        super(TimeBasedHeap, self).__init__(from_list=())

    def put(self, *args):
        """
        Put an item of heap.

        Pass timestamp, item or just an item for default time
        """
        assert len(args) in (1, 2)

        if len(args) == 1:
            timestamp, item = self.default_clock_source(), args[0]
        else:
            timestamp, item = args

        assert timestamp is not None
        self.push((timestamp, item))

    def pop_less_than(self, less: tp.Optional[tp.Union[int, float]] = None) -> tp.Iterator:
        """
        Return all elements less (sharp inequality) than particular value.

        This changes state of the heap
        :param less: value to compare against
        :return: Iterator
        """

        if less is None:
            less = self.default_clock_source()

        assert less is not None

        while self:
            if self.heap[0][0] >= less:
                return
            yield self.pop()

    def remove(self, item):
        """
        Remove all things equal to item
        """
        self.filtermap(filter_fun=lambda i: i != item)
