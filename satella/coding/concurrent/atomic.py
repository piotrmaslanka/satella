import typing as tp

from .monitor import Monitor
from .thread import Condition
from ...exceptions import WouldWaitMore
from ...time import measure

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

    def wait(self, timeout: tp.Optional[float] = None, throw_exception: bool = True):
        """
        Block until the atomic number changes it's value.

        :param timeout: maximum time to wait. None means wait indefinitely
        :param throw_exception: whether to throw WouldWaitMore on timeout
        :raises WouldWaitMore: the value hasn't changed within the timeout
        """
        try:
            self.condition.wait(timeout)
        except WouldWaitMore:
            if throw_exception:
                raise

    def __repr__(self) -> str:
        return str(self)

    @Monitor.synchronized
    def __str__(self) -> str:
        return 'AtomicNumber(%s)' % (self.value,)

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
    def __le__(self, other: Number):
        return self.value <= other

    @Monitor.synchronized
    def __iadd__(self, other: Number) -> 'AtomicNumber':
        self.value += other
        self.condition.notify_all()
        return self

    @Monitor.synchronized
    def __pow__(self, power, modulo=None):
        return self.value.__pow__(power, modulo)

    @Monitor.synchronized
    def __ipow__(self, other):
        self.value **= other
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
    def __floordiv__(self, other: Number) -> Number:
        return self.value // other

    @Monitor.synchronized
    def __itruediv__(self, other: Number) -> 'AtomicNumber':
        self.value /= other
        self.condition.notify_all()
        return self

    @Monitor.synchronized
    def __ifloordiv__(self, other: Number) -> 'AtomicNumber':
        self.value //= other
        self.condition.notify_all()
        return self

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

    @Monitor.synchronized
    def __neg__(self) -> Number:
        return -self.value

    def wait_until_equal(self, v: Number, timeout: tp.Optional[float] = None) -> None:
        """
        Wait until the value of this number equals v.

        :param v: value to compare this number against
        :param timeout: maximum time to wait
        :raise WouldWaitMore: timeout expired without the value becoming equal to target
        """
        if timeout is None:
            while True:
                if self == v:
                    break
                self.wait()
        else:
            with measure() as measurement:
                while measurement() < timeout:
                    time_remaining = timeout - measurement()
                    if self == v:
                        break
                    self.wait(time_remaining, throw_exception=False)

                with Monitor.acquire(self):
                    if self.value != v:
                        raise WouldWaitMore()
