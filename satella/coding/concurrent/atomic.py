import typing as tp
from .monitor import Monitor
from .thread import Condition


Number = tp.Union[int, float]


class AtomicNumber(Monitor):
    """
    An atomic number. Note that the class is not hashable and for a reason, since it's value
    might change in time. So in this case this is more of like a container for numbers.

    Treat it like a normal number, except all operations are executed atomically.

    You can also wait for it to change it's value, via wait().

    You change it's value in the following way:

    >>> a = AtomicNumber()
    >>> a += 2

    Note that if the number if used in an expression, such as

    >>> b = a + 2

    Then a normal number will be returned
    """
    __slots__ = ('value', 'condition')

    def __init__(self, v: Number = 0):
        super().__init__()
        self.value = v
        self.condition = Condition()

    def wait(self, timeout: tp.Optional[float] = None):
        """
        Block until the atomic number changes it's value.

        :raises WouldWaitMore: the value hasn't changed within the timeout
        """
        self.condition.wait(timeout)

    @Monitor.synchronized
    def __gt__(self, other: Number):
        return self.value > other

    @Monitor.synchronized
    def __ge__(self, other: Number):
        return self.value >= other

    @Monitor.synchronized
    def __lt__(self, other: Number):
        return self.value < other

    @Monitor.synchronized
    def __len__(self, other: Number):
        return self.value <= other

    @Monitor.synchronized
    def __iadd__(self, other: Number) -> 'AtomicNumber':
        self.value += other
        self.condition.notify_all()
        return self

    @Monitor.synchronized
    def __add__(self, other: Number) -> Number:
        return self.value + other

    @Monitor.synchronized
    def __sub__(self, other: Number) -> Number:
        return self.value - other

    @Monitor.synchronized
    def __mul__(self, other: Number) -> Number:
        return self.value * other

    @Monitor.synchronized
    def __truediv__(self, other: Number) -> Number:
        return self.value / other

    @Monitor.synchronized
    def __isub__(self, other: int) -> 'AtomicNumber':
        self.value -= other
        self.condition.notify_all()
        return self

    @Monitor.synchronized
    def __imul__(self, other: int) -> 'AtomicNumber':
        self.value *= other
        self.condition.notify_all()
        return self

    @Monitor.synchronized
    def __eq__(self, other: tp.Union['AtomicNumber', Number]) -> bool:
        if isinstance(other, AtomicNumber):
            with Monitor.acquire(other):
                return self.value == other.value
        else:
            return self.value == other

    @Monitor.synchronized
    def __int__(self) -> int:
        return int(self.value)

    @Monitor.synchronized
    def __float__(self) -> float:
        return float(self.value)

    @Monitor.synchronized
    def __bool__(self) -> bool:
        return bool(self.value)

    @Monitor.synchronized
    def __abs__(self) -> Number:
        return abs(self.value)
