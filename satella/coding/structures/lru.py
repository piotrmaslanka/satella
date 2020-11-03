import typing as tp
from collections import OrderedDict

T = tp.TypeVar('T', covariant=tp.Hashable)


class LRU(tp.Generic[T]):
    """
    A class to track least recently used objects.
    """

    def __init__(self):
        self.od = OrderedDict()

    def __contains__(self, item: T) -> bool:
        return item in self.od

    def __len__(self):
        return len(self.od)

    def add(self, item: T) -> None:
        self.od[item] = True

    def remove(self, item: T) -> None:
        del self.od[item]

    def mark_as_used(self, item: T):
        if item not in self.od:
            self.od[item] = True
        else:
            self.od.move_to_end(item)

    def get_item_to_evict(self) -> T:
        """
        Return a least recently used object
        """
        return self.od.popitem(False)[0]
