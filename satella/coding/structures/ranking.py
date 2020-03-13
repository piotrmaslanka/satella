import logging
import typing as tp

from satella.coding.recast_exceptions import rethrow_as
logger = logging.getLogger(__name__)


__all__ = ['Ranking']


T = tp.TypeVar('T')
Id = tp.NewType('Id', int)


# todo optimize this
class Ranking(tp.Generic[T]):
    """
    A set of objects with them being ranked by their single property with the assumption that this
    property changes only when we want to.

    Positions are counted from 0, where 0 has the least key value.

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
    __slots__ = ('items', 'key', 'ranking', 'reverse_ranking')

    def __init__(self, items: tp.List[T], key: tp.Callable[[T], int]):
        self.items = items
        self.key = key
        self.ranking = {}           # tp.Dict[Id, int]
        self.reverse_ranking = {}   # tp.Dict[int, T]
        self.recalculate_ranking()

    def recalculate_ranking(self) -> None:
        ranking = [(self.key(t), t) for t in self.items]       # type: tp.List[tp.Tuple[int, T]]
        ranking.sort()
        self.ranking = {}
        self.reverse_ranking = {}
        for position, ranking_row in enumerate(ranking):
            t = ranking_row[1]
            self.ranking[id(t)] = position
            self.reverse_ranking[position] = t

    def add(self, item: T) -> None:
        """
        Add a single element to the ranking and recalculate it
        """
        self.add_many([item])

    def remove(self, item: T) -> None:
        """
        Remove a single element from the ranking and recalculate it
        """
        self.remove_many([item])

    def add_many(self, items: tp.List[T]) -> None:
        """
        Add many elements to the ranking and recalculate it
        """
        self.items.extend(items)
        self.recalculate_ranking()

    def remove_many(self, items: tp.List[T]) -> None:
        """
        Remove multiple elements from the ranking and recalculate it
        """
        for item in items:
            self.items.remove(item)
        self.recalculate_ranking()

    @rethrow_as(KeyError, ValueError)
    def get_position_of(self, item: T) -> int:
        """
        Return the position in the ranking of element item

        :param item: element to return the position for
        :return: position
        :raises ValueError: this element is not in the ranking
        """
        return self.ranking[id(item)]

    def __getitem__(self, item: int) -> T:
        """
        Return n-th item in ranking.

        :param item: position in ranking. Can be negative
        """
        return self.reverse_ranking[item % len(self.ranking)]

    def get_sorted(self) -> tp.Iterator[T]:
        """
        Return all the elements sorted from the least key value to the highest key value
        """
        for i in range(len(self.ranking)):
            yield self.reverse_ranking[i]
