from .monitor import Monitor
from ...exceptions import AlreadyAllocated


class SequentialIssuer(Monitor):
    """
    A classs that issues an monotonically increasing value.

    :param start: start issuing IDs from this value

    :ivar start: next value to be issued
    """
    __slots__ = ('start', )

    def __init__(self, start: int = 0):
        super().__init__()
        self.start = start

    @Monitor.synchronized
    def issue(self) -> int:
        """
        Just issue a next identifier

        :return: a next identifier
        """
        try:
            return self.start
        finally:
            self.start += 1

    @Monitor.synchronized
    def no_less_than(self, no_less_than: int) -> int:
        """
        Issue an int, which is no less than a given value

        :param no_less_than: value that the returned id will not be less than this
        :return: an identifier, no less than no_less_than
        """
        try:
            if self.start > no_less_than:
                return self.start
                self.start += 1
            else:
                self.start = no_less_than
                return self.start
        finally:
            self.start += 1


class IDAllocator(Monitor):
    """
    Reusable ID allocator

    You can use it to requisition ints from a pool, and then free their ints, permitting
    them to be reused.

    Thread-safe.

    :param start_at: the lowest integer that the allocator will return
    """
    __slots__ = ('start_at', 'ints_allocated', 'free_ints', 'bound')

    def __init__(self, start_at: int = 0):
        super().__init__()
        self.start_at = start_at
        self.ints_allocated = set()
        self.free_ints = set()
        self.bound = 0

    def _extend_the_bound_to(self, x: int):
        for i in range(self.bound, x):
            self.free_ints.add(i)
        self.bound = x

    @Monitor.synchronized
    def mark_as_free(self, x: int):
        """
        Mark x as free

        :param x: int to free
        :raises ValueError: x was not allocated or less than start_at
        """
        if x < self.start_at:
            raise ValueError('%s is less than start_at' % (x,))
        x -= self.start_at
        if x not in self.ints_allocated:
            raise ValueError('%s was not allocated' % (x,))
        self.ints_allocated.remove(x)
        self.free_ints.add(x)

    @Monitor.synchronized
    def allocate_int(self) -> int:
        """
        Return a previously unallocated int, and mark it as allocated

        :return: an allocated int
        """
        if not self.free_ints:
            self._extend_the_bound_to(self.bound + 10)
        x = self.free_ints.pop()
        self.ints_allocated.add(x)
        return x + self.start_at

    @Monitor.synchronized
    def mark_as_allocated(self, x: int):
        """
        Mark given x as allocated

        :param x: x to mark as allocated
        :raises AlreadyAllocated: x was already allocated
        :raises ValueError: x is less than start_at
        """
        if x < self.start_at:
            raise ValueError('%s is less than start_at' % (x,))
        x -= self.start_at
        if x >= self.bound:
            self._extend_the_bound_to(x + 1)
            self.free_ints.remove(x)
            self.ints_allocated.add(x)
        else:
            if x in self.ints_allocated:
                raise AlreadyAllocated()
            self.free_ints.remove(x)
            self.ints_allocated.add(x)
