import collections
import typing as tp

from .sorted_list import SortedList

T = tp.TypeVar('T')


class Ranking(tp.Generic[T]):
    """
    A set of objects with them being ranked by their single property with the assumption that this
    property changes only when we want to.

    Positions are counted from 0, where 0 has the least key value.

    Essentially, this is a SortedList with the option to query at which position can be given
    element found.

    Example usage:

    >>> Entry = collections.namedtuple('Entry', ('key', ))
    >>> e1 = Entry(2)
    >>> e2 = Entry(3)
    >>> e3 = Entry(5)
    >>> ranking = Ranking([e1, e2, e3], lambda e: e.key)
    >>> assert ranking[0] == e1     # Get the first element
    >>> assert ranking[-1] == e3    # Get the last element
    >>> assert ranking.get_position_of(e1) == 0
    """
    __slots__ = ('items', 'key', 'ranking', 'element_to_position')

    def __init__(self, items: tp.List[T], key: tp.Callable[[T], int]):
        self.items = items
        self.key = key
        self.ranking = SortedList(items, key=key)  # type: SortedList[T]
        self.element_to_position = {}  # type: tp.Dict[int, int]
        for position, item in enumerate(self.ranking):
            self.element_to_position[id(item)] = position

    def calculate_ranking_for(self, item: T) -> int:
        return self.element_to_position[id(item)]

    def add(self, item: T) -> None:
        """
        Add a single element to the ranking and recalculate it
        """
        index = self.ranking.add(item)
        for position, item in enumerate(self.ranking[index:], start=index):
            self.element_to_position[id(item)] = position

    def remove(self, item: T) -> None:
        """
        Remove a single element from the ranking and recalculate it
        """
        index = self.ranking.index(item)
        self.ranking.remove(item)
        for position, item in enumerate(self.ranking[index:], start=index):
            self.element_to_position[id(item)] = position

    def get_position_of(self, item: T) -> int:
        """
        Return the position in the ranking of element item

        :param item: element to return the position for
        :return: position
        :raises ValueError: this element is not in the ranking
        """
        return self.ranking.index(item)

    def __getitem__(self, item: int) -> T:
        """
        Return n-th item in ranking.

        :param item: position in ranking. Can be negative, or even a slice
        """
        return self.ranking[item]

    def get_sorted(self) -> tp.Iterator[T]:
        """
        Return all the elements sorted from the least key value to the highest key value
        """
        yield from self.ranking
