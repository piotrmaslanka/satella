import collections
import typing as tp
from satella.coding.typing import T, K

Ka = tp.TypeVar('Ka', covariant=tp.Hashable)


class NDimensionalStructure(tp.Generic[Ka]):
    """
    A structure having n dimensions. It does this by keying elements in such a way that a key
    is a frozenset, and each element of the set describes a dimension.

    Note that items must be hashable.

    :param key_getter: a callable that obtains the key for given element. The default implementation
        assumes that items are frozen sets themselves.
    """
    __slots__ = ('indices', 'key_getter')

    def __init__(self, elements: tp.Iterable[Ka],
                 key_getter: tp.Callable[[Ka], tp.FrozenSet[K]] = lambda y: y):
        self.indices = collections.defaultdict(list)   # type: tp.Dict[tp.FrozenSet[K], tp.List[T]]
        self.key_getter = key_getter
        for elem in elements:
            self.add(elem)

    def __len__(self) -> int:
        elements = set()
        for elem_list in self.indices.values():
            elements.update(elem_list)
        return len(elements)

    def add(self, item: Ka) -> None:
        for member in self.key_getter(item):
            self.indices[member].append(item)

    def intersection(self, keys: tp.Set[K]) -> 'NDimensionalStructure[T]':
        iter_keys = iter(keys)
        try:
            first_key = next(iter_keys)
        except StopIteration:
            return self

        output = set(self.indices[first_key])

        for key in iter_keys:
            output = output.intersection(self.indices[key])

        return NDimensionalStructure(output, self.key_getter)


