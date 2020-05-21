import collections
import typing as tp

T = tp.TypeVar('T')


class SortedList(tp.Generic[T]):
    """
    An always-sorted sort of a set

    It is assumed that keys of constituent elements don't change.

    list[0] will have the smallest element, and list[-1] the biggest

    :param items: items to construct the list with
    :param key: a callable[T]->int that builds the key of the sort
    """
    __slots__ = ('items', 'keys', 'key')

    def __init__(self, items: tp.Iterable[T] = (), key: tp.Callable[[T], int] = lambda a: a):
        sort = sorted((key(item), item) for item in items)
        self.items = SliceableDeque(a[1] for a in sort)  # type: SliceableDeque[T]
        self.keys = collections.deque(a[0] for a in sort)  # type: collections.deque[int]
        self.key = key  # type: tp.Callable[[T], int]

    def __contains__(self, item: T) -> bool:
        return item in self.items

    def pop(self) -> T:
        """Return the highest element, removing it from the list"""
        self.keys.pop()
        return self.items.pop()

    def popleft(self) -> T:
        """Return the smallest element, removing it from the list"""
        self.keys.popleft()
        return self.items.popleft()

    def __iter__(self) -> tp.Iterator[T]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def index(self, other: T) -> int:
        """Return index at which given value has been placed"""
        return self.items.index(other)

    def extend(self, elements: tp.Iterable[T]):
        """Adds multiple elements to this list"""
        for elem in elements:
            self.add(elem)

    def __getitem__(self, item: tp.Union[slice, int]) -> tp.Union[T, tp.Iterator[T]]:
        return self.items[item]

    def remove(self, other: T) -> None:
        """
        Remove an element from the list

        :param other: element to remove
        :raises ValueError: element not in list
        """
        index = self.items.index(other)  # throws ValueError
        del self.items[index]
        del self.keys[index]

    def add(self, other: T) -> int:
        """
        Add an element. Returns the index at which it was inserted.

        :param other: element to insert
        :return: index that the entry is available now at
        """
        key_value = self.key(other)

        for index in range(len(self.keys)):
            if key_value <= self.keys[index]:
                break
        else:
            index = len(self.keys)

        self.items.insert(index, other)
        self.keys.insert(index, key_value)

        return index


class SliceableDeque(collections.abc.MutableSequence, tp.Generic[T]):
    """
    A collections.deque that supports slicing.

    Just note that it will return a p_gen upon being sliced!
    """
    __slots__ = ('deque',)

    def __bool__(self) -> bool:
        return bool(self.deque)

    def insert(self, i: int, item: T):
        self.deque.insert(i, item)

    def __init__(self, *args, **kwargs):
        self.deque = collections.deque(*args, **kwargs)

    def __setitem__(self, key: int, value: T) -> None:
        self.deque[key] = value

    def __delitem__(self, key: int) -> None:
        del self.deque[key]

    def __iter__(self) -> tp.Iterator[T]:
        return iter(self.deque)

    def __len__(self) -> int:
        return len(self.deque)

    def __reversed__(self) -> tp.Iterator[T]:
        return reversed(self.deque)

    def __contains__(self, item: T) -> bool:
        return item in self.deque

    def __getattr__(self, item: str):
        return getattr(self.deque, item)

    def __getitem__(self, item) -> tp.Union[tp.Iterator[T], T]:
        """Return either one element, or a p_gen over a slice"""
        tot_length = len(self)
        if type(item) is slice:
            start, stop, step = item.indices(tot_length)

            def generator():
                for index in range(start, stop, step):
                    yield self.deque[index]

            return generator()
        else:
            return self.deque[item]
