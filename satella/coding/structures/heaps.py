import collections
import copy
import heapq
import time
import typing as tp

from ..recast_exceptions import rethrow_as
from ..decorators import wraps

T = tp.TypeVar('T')
Number = tp.Union[int, float]


def _extras_to_one(fun):
    @wraps(fun)
    def inner(self, a, *args, **kwargs):
        return fun(self, ((a,) + args) if len(args) > 0 else a, **kwargs)

    return inner


class Heap(collections.UserList, tp.Generic[T]):
    """
    Sane heap as object - not like heapq.

    Goes from lowest-to-highest (first popped is smallest).
    Standard Python comparision rules apply.

    Not thread-safe
    """

    def __init__(self, from_list: tp.Optional[tp.Iterable[T]] = None):
        super().__init__(from_list)
        heapq.heapify(self.data)

    def push_many(self, items: tp.Iterable[T]) -> None:
        for item in items:
            self.push(item)

    def pop_item(self, item: T) -> T:
        """
        Pop an item off the heap, maintaining the heap invariant

        :raise ValueError: element not found
        """
        self.data.remove(item)      # raises: ValueError
        heapq.heapify(self.data)
        return item

    @_extras_to_one
    def push(self, item: T) -> None:
        """
        Use it like:

        >>> heap.push(3)

        or:

        >>> heap.push(4, myobject)
        """
        heapq.heappush(self.data, item)

    def __deepcopy__(self, memo) -> 'Heap':
        return self.__class__(copy.deepcopy(self.data, memo))

    def __copy__(self) -> 'Heap':
        return self.__class__(copy.copy(self.data))

    def __iter__(self) -> tp.Iterator[T]:
        return self.data.__iter__()

    def pop(self) -> T:
        """
        Return smallest element of the heap.

        :raises IndexError: on empty heap
        """
        return heapq.heappop(self.data)

    def filter_map(self, filter_fun: tp.Optional[tp.Callable[[T], bool]] = None,
                   map_fun: tp.Optional[tp.Callable[[T], tp.Any]] = None):
        """
        Get only items that return True when condition(item) is True. Apply a
         transform: item' = item(condition) on
        the rest. Maintain heap invariant.
        """
        heap = filter(filter_fun, self.data) if filter_fun else self.data
        heap = map(map_fun, heap) if map_fun else heap
        heap = list(heap) if not isinstance(heap, list) else heap
        self.data = heap
        heapq.heapify(self.data)

    def __bool__(self) -> bool:
        """
        Is this empty?
        """
        return len(self.data) > 0

    def iter_ascending(self) -> tp.Iterable[T]:
        """
        Return an iterator returning all elements in this heap sorted ascending.
        State of the heap is not changed
        """
        heap = copy.copy(self.data)
        while heap:
            yield heapq.heappop(heap)

    def iter_descending(self) -> tp.Iterable[T]:
        """
        Return an iterator returning all elements in this heap sorted descending.
        State of the heap is not changed.

        This loads all elements of the heap into memory at once, so be careful.
        """
        return reversed(list(self.iter_ascending()))

    def __eq__(self, other: 'Heap') -> bool:
        return self.data == other.data

    def __len__(self) -> int:
        return len(self.data)

    def __str__(self) -> str:
        return '<satella.coding.Heap: %s elements>' % (len(self, ))

    def __repr__(self) -> str:
        return u'<satella.coding.Heap>'

    def __contains__(self, item: T) -> bool:
        return item in self.data


class SetHeap(Heap):
    """
    A heap with additional invariant that no two elements are the same.

    Optimized for fast insertions and fast __contains__

    #notthreadsafe
    """

    def __init__(self, from_list: tp.Optional[tp.Iterable[T]] = None):
        super().__init__(from_list=from_list)
        self.set = set(self.data)

    def push(self, item: T):
        if item not in self.set:
            super().push(item)
            self.set.add(item)

    def pop(self) -> T:
        item = super().pop()
        self.set.remove(item)
        return item

    def __contains__(self, item: T) -> bool:
        return item in self.set

    def filter_map(self, filter_fun: tp.Optional[tp.Callable[[T], bool]] = None,
                   map_fun: tp.Optional[tp.Callable[[T], tp.Any]] = None):
        super().filter_map(filter_fun=filter_fun, map_fun=map_fun)
        self.set = set(self.data)


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
    * time.monotonic

    Default is time.monotonic

    #notthreadsafe
    """

    def __repr__(self):
        return '<satella.coding.TimeBasedHeap with %s elements>' % (len(self.data),)

    def items(self) -> tp.Iterable[tp.Tuple[Number, T]]:
        """
        Return an iterable, but WITHOUT timestamps (only items), in
        unspecified order
        """
        return (ob for ts, ob in self.data)

    def __init__(self, default_clock_source: tp.Callable[[], Number] = None):
        """
        Initialize an empty heap
        """
        self.default_clock_source = default_clock_source or time.monotonic
        super().__init__(from_list=())

    def pop_timestamp(self, timestamp: Number) -> T:
        """
        Get first item with given timestamp, while maintaining the heap invariant

        :raise ValueError: element not found
        """
        for index, item in enumerate(self.data):
            if item[0] == timestamp:
                ts, item = self.data.pop(index)
                heapq.heapify(self.data)
                return item
        raise ValueError('Element not found!')

    def get_timestamp(self, item: T) -> Number:
        """
        Return the timestamp for given item
        """
        for ts, elem in self.data:
            if elem[1] == item:
                return ts

    def pop_item(self, item: T) -> tp.Tuple[Number, T]:
        """
        Pop an item off the heap, maintaining the heap invariant.

        The item will be a second part of the tuple

        :raise ValueError: element not found
        """
        for index, elem in enumerate(self.data):
            if elem[1] == item:
                obj = self.data.pop(index)
                heapq.heapify(self.data)
                return obj
        raise ValueError('Element not found!')

    def put(self, timestamp_or_value: tp.Union[T, Number],
            value: tp.Optional[T] = None) -> None:
        """
        Put an item on heap.

        Pass timestamp, item or just an item for default time
        """
        if value is None:
            timestamp, item = self.default_clock_source(), timestamp_or_value
        else:
            timestamp, item = timestamp_or_value, value

        assert timestamp is not None
        self.push((timestamp, item))

    def pop_less_than(self, less: tp.Optional[Number] = None) -> tp.Iterator[tp.Tuple[Number, T]]:
        """
        Return all elements less (sharp inequality) than particular value.

        This changes state of the heap

        :param less: value to compare against
        :return: a Generator
        """

        if less is None:
            less = self.default_clock_source()

        assert less is not None, 'Default clock source returned None!'

        while self:
            if self.data[0][0] >= less:
                return
            yield self.pop()

    def remove(self, item: T) -> None:
        """
        Remove all things equal to item
        """
        self.filter_map(filter_fun=lambda i: i[1] != item)


class TimeBasedSetHeap(Heap):
    """
    A heap of items sorted by timestamps, with such invariant that every item can appear at most once.

    It is easy to ask for items, whose timestamps are LOWER than a value, and
    easy to remove them.

    Can be used to implement a scheduling service, ie. store jobs, and each
    interval query
    which of them should be executed. This loses time resolution, but is fast.

    Can use current time with put/pop_less_than.
    Use default_clock_source to pass a callable:

    * time.time
    * time.monotonic

    Default is time.monotonic

    #notthreadsafe
    """

    def __repr__(self):
        return '<satella.coding.TimeBasedSetHeap with %s elements>' % (len(self.data),)

    @rethrow_as(KeyError, ValueError)
    def get_timestamp(self, item: T) -> Number:
        """
        Return the timestamp for given item

        :raises ValueError: item not found
        """
        return self.item_to_timestamp[item]

    def items(self) -> tp.Iterable[T]:
        """
        Return an iterable, but WITHOUT timestamps (only items), in
        unspecified order
        """
        return (ob for ts, ob in self.data)

    def __init__(self, default_clock_source: tp.Callable[[], Number] = None):
        """
        Initialize an empty heap
        """
        self.default_clock_source = default_clock_source or time.monotonic
        super().__init__(from_list=())
        self.item_to_timestamp = {}

    def pop_timestamp(self, timestamp: Number) -> T:
        """
        Pop an arbitary object (in case there's two) item with given timestamp,
        while maintaining the heap invariant

        :raise ValueError: element not found
        """
        for index, item in enumerate(self.data):
            if item[0] == timestamp:
                obj = self.data.pop(index)
                del self.item_to_timestamp[obj[1]]
                heapq.heapify(self.data)
                return obj[1]
        raise ValueError('Element not found!')

    def pop_item(self, item: T) -> tp.Tuple[Number, T]:
        """
        Pop an item off the heap, maintaining the heap invariant.

        The item will be a second part of the tuple

        :raise ValueError: element not found
        """
        for index, elem in enumerate(self.data):
            if elem[1] == item:
                obj = self.data.pop(index)
                heapq.heapify(self.data)
                del self.item_to_timestamp[obj[1]]
                return obj
        raise ValueError('Element not found!')

    def push(self, item: tp.Tuple[Number, T]) -> None:
        if item[1] in self.item_to_timestamp:
            self.pop_item(item[1])

        super().push(item)
        self.item_to_timestamp[item[1]] = item[0]

    def pop(self) -> tp.Tuple[Number, T]:
        item = super().pop()
        del self.item_to_timestamp[item[1]]
        return item

    def put(self, timestamp_or_value: tp.Union[T, Number],
            value: tp.Optional[T] = None) -> None:
        """
        Put an item on heap.

        Pass timestamp, item or just an item for default time
        """
        if value is None:
            timestamp, item = self.default_clock_source(), timestamp_or_value
        else:
            timestamp, item = timestamp_or_value, value

        assert timestamp is not None
        self.push((timestamp, item))

    def pop_less_than(self, less: tp.Optional[Number] = None) -> tp.Iterator[tp.Tuple[Number, T]]:
        """
        Return all elements less (sharp inequality) than particular value.

        This changes state of the heap

        :param less: value to compare against
        :return: a Generator
        """

        if less is None:
            less = self.default_clock_source()

        assert less is not None, 'Default clock source returned None!'

        while self:
            if self.data[0][0] >= less:
                return
            yield self.pop()

    def remove(self, item: T) -> None:
        """
        Remove all things equal to item
        """
        self.filter_map(filter_fun=lambda i: i[1] != item)