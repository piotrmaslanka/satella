import collections
import copy
import heapq
import typing as tp

from satella.coding.decorators.decorators import wraps
from satella.coding.typing import T, Predicate


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
        self.data.remove(item)  # raises: ValueError
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

    def __deepcopy__(self, memo={}) -> 'Heap':
        return self.__class__(copy.deepcopy(self.data, memo=memo))

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

    def filter_map(self, filter_fun: tp.Optional[Predicate[T]] = None,
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

    Note that elements you insert in this must be eq-able and hashable, ie. you can put them in a
    dict.

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

    def filter_map(self, filter_fun: tp.Optional[Predicate[T]] = None,
                   map_fun: tp.Optional[tp.Callable[[T], tp.Any]] = None):
        super().filter_map(filter_fun=filter_fun, map_fun=map_fun)
        self.set = set(self.data)
