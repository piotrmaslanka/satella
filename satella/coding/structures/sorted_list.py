import logging
import typing as tp
import collections

logger = logging.getLogger(__name__)

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
        self.items = collections.deque(a[1] for a in sort)
        self.keys = collections.deque(a[0] for a in sort)
        self.key = key

    def __contains__(self, item: T) -> bool:
        return item in self.items

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

    def __getitem__(self, item: int) -> tp.Union[T, tp.List[T]]:
        return self.items[item]

    def remove(self, other: T) -> None:
        """
        Remove an element from the list

        :param other: element to remove
        :raises ValueError: element not in list
        """
        index = self.items.index(other)     # throws ValueError
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
