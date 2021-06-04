import typing as tp
from collections import deque

from satella.coding.typing import T


class PushIterable(tp.Generic[T]):
    """
    An iterable that you can add elements to it's head, and they will be popped
    before this iterable is consumed when a pop is called.

    Example:

    .. code-block:: python

        a = PushIterable([1, 2, 3])
        assert a.pop() == 1
        a.push(0)
        assert a.pop() == 0
        assert a.pop() == 2
        a.push(0)
        a.push(1)
        assert a.pop() == 1
        assert a.pop() == 0
        a.push_left(0)
        a.push_left(1)
        assert a.pop() == 0
        assert a.pop() == 1
        assert a.pop() == 3
        assertRaises(StopIteration, a.pop)
    """

    def __init__(self, iterable: tp.Iterable[T]):
        self.iterable = iter(iterable)
        self.collection = deque()

    def pop(self) -> T:
        """
        Return next element from the stack
        :return: a next element
        """
        if not self.collection:
            return next(self.iterable)
        else:
            return self.collection.pop()

    def __iter__(self):
        return self

    def __next__(self) -> T:
        return self.pop()

    def push(self, item: T) -> None:
        """
        Push an item so that next pop will retrieve this item

        :param item: item to push
        """
        self.collection.append(item)

    def push_left(self, item):
        """
        Push an item so that last pop from internal buffer will retrieve this item

        :param item: item to push
        """
        self.collection.appendleft(item)
