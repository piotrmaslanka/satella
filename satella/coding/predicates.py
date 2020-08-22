import typing as tp
import operator

__all__ = ['x']


def make_operation_two_args(operation_two_args: tp.Callable[[tp.Any, tp.Any], tp.Any]):
    def operation(self, a) -> 'Predicate':
        if isinstance(a, Predicate):
            def op(v):
                return operation_two_args(self(v), a(v))
        else:
            def op(v):
                return operation_two_args(self(v), a)
        return Predicate(op)
    return operation


def make_operation_single_arg(operation):
    def operation_v(self):
        def operate(v):
            return operation(v)
        return Predicate(operate)
    return operation_v


def _has_keys(a, keys):
    for key in keys:
        if key not in a:
            return False
    return True


def _one_of(a, values):
    return a in values


class Predicate:
    __slots__ = ('operation', )

    def __init__(self, operation: tp.Callable[[tp.Any], tp.Any]):
        self.operation = operation

    def __call__(self, v):
        return self.operation(v)

    def has_keys(self, *keys):
        """
        Return a predicate checking whether this value has provided keys
        """
        return make_operation_two_args(_has_keys)(self, keys)

    def one_of(self, *values):
        """
        Return a predicate checking if x is amongst values
        """
        return make_operation_two_args(_one_of)(self, values)

    def inside(self, value):
        """
        Return a predicate checking if x is inside value
        """
        return make_operation_two_args(operator.contains)(self, value)

    def instanceof(self, instance):
        """
        Return a predicate checking whether this value is an instance of instance
        """
        return make_operation_two_args(isinstance)(self, instance)

    length = make_operation_single_arg(len)

    __contains__ = make_operation_two_args(operator.contains)
    __getattr__ = make_operation_two_args(getattr)
    __getitem__ = make_operation_two_args(lambda a, b: a[b])
    __eq__ = make_operation_two_args(operator.eq)
    __ne__ = make_operation_two_args(operator.ne)
    __lt__ = make_operation_two_args(operator.lt)
    __gt__ = make_operation_two_args(operator.gt)
    __le__ = make_operation_two_args(operator.le)
    __ge__ = make_operation_two_args(operator.ge)
    __add__ = make_operation_two_args(operator.add)
    __sub__ = make_operation_two_args(operator.sub)
    __mul__ = make_operation_two_args(operator.mul)
    __and__ = make_operation_two_args(operator.and_)
    __or__ = make_operation_two_args(operator.or_)
    __xor__ = make_operation_two_args(operator.xor)
    __neg__ = make_operation_single_arg(lambda y: -y)
    __invert__ = make_operation_single_arg(operator.invert)
    __abs__ = make_operation_single_arg(abs)
    __int__ = make_operation_single_arg(int)
    __float__ = make_operation_single_arg(float)
    __complex__ = make_operation_single_arg(complex)
    __str__ = make_operation_single_arg(str)
    __truediv__ = make_operation_two_args(operator.__truediv__)
    __floordiv__ = make_operation_two_args(operator.floordiv)
    __mod__ = make_operation_two_args(operator.mod)


x = Predicate(lambda y: y)
