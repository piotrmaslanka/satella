import heapq
import time
import typing as tp

from satella.coding.recast_exceptions import rethrow_as
from .base import Heap

Number = tp.Union[int, float]
T = tp.TypeVar('T')


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

    def __repr__(self) -> str:
        return '<satella.coding.TimeBasedHeap with %s elements>' % (len(self.data),)

    def items(self) -> tp.Iterable[tp.Tuple[Number, T]]:
        """
        Return an iterable, but WITHOUT timestamps (only items), in
        unspecified order
        """
        return (ob for ts, ob in self.data)

    def __init__(self, default_clock_source: tp.Callable[[], Number] = time.monotonic):
        """
        Initialize an empty heap
        """
        self.default_clock_source = default_clock_source
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

        :param less: value to compare against. If left at default, it will be the
            default clock source specified at construction.
        :return: an Iterator
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

    Note that elements you insert in this must be eq-able and hashable, ie. you can put them in a dict.

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

    def __repr__(self) -> str:
        return '<satella.coding.TimeBasedSetHeap with %s elements>' % (len(self.data),)

    @rethrow_as(KeyError, ValueError)
    def get_timestamp(self, item: T) -> Number:
        """
        Return the timestamp for given item

        :raises ValueError: item not found
        """
        return self.item_to_timestamp[item]

    def items(self) -> tp.Iterator[T]:
        """
        Return an iterator, but WITHOUT timestamps (only items), in
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
