import typing as tp

from satella.coding.structures import Heap
from satella.coding.typing import K, V


class merge_list(tp.Iterator[tp.Tuple[K, V]]):
    """
    Merge two sorted lists.

    This is an iterator which consumes elements as they are required.

    Each list must be of type tuple/2 with the first element being the key.
    The list has to be sorted by this value, ascending.

    When the algorithm encounters two identical keys, it calls merge_function on it's
    result and inserts the result.

    :param lists: lists to sort
    :param merge_function: a callable that accepts two pieces of the tuple and returns a result
    :return: an resulting iterator
    """
    __slots__ = ('merge_func', 'its', 'heap', 'available_lists',
                 'k', 'v', 'i', 'closed')

    def __iter__(self):
        return self

    def __init__(self, *lists: tp.Iterator[tp.Tuple[K, V]],
                 merge_function: tp.Callable[[V, V], V]):
        self.its = [iter(y) for y in lists]
        self.merge_func = merge_function
        self.available_lists = set()
        self.heap = Heap()
        self.closed = False

        for i, it in enumerate(self.its):
            try:
                self.heap.push((*next(it), i))
                self.available_lists.add(i)
            except StopIteration:
                pass
        try:
            self.k, self.v, self.i = self.pop()
        except IndexError:
            self.closed = True

    def __next__(self):
        if self.closed:
            raise StopIteration()

        try:
            k2, v2, i2 = self.pop()
        except IndexError:
            self.closed = True
            return self.k, self.v

        if k2 == self.k:
            self.v = self.merge_func(self.v, v2)
            return next(self)

        try:
            return self.k, self.v
        finally:
            self.k, self.v, self.i = k2, v2, i2

    def pop(self):
        k, v, i = self.heap.pop()
        if i in self.available_lists:
            try:
                k2, v2 = next(self.its[i])
                self.heap.push((k2, v2, i))
            except StopIteration:
                self.available_lists.remove(i)
        return k, v, i
