import operator
import typing as tp

from satella.coding.typing import Predicate
from satella.configuration.schema import Descriptor

__all__ = ['x', 'build_structure', 'PredicateClass']

import warnings


def _nop(v: tp.Any) -> tp.Any:
    return v


def make_operation_two_args(operation_two_args: tp.Callable[[tp.Any, tp.Any], tp.Any],
                            docstring: tp.Optional[str] = None,
                            swap_order: bool = False) -> Predicate:
    def operation(self, a: tp.Callable) -> Predicate:
        if isinstance(a, PredicateClass):
            if swap_order:
                def op(v):
                    return operation_two_args(a(v), self(v))

                return PredicateClass(op)
            else:
                def op(v):
                    return operation_two_args(self(v), a(v))

                return PredicateClass(op)
        else:
            if swap_order:
                def op(v):
                    return operation_two_args(a, self(v))

                return PredicateClass(op)
            else:
                def op(v):
                    return operation_two_args(self(v), a)

                return PredicateClass(op)

    if docstring:
        operation.__doc__ = docstring

    return operation


def make_operation_single_arg(operation: tp.Callable[[tp.Any], tp.Any],
                              docstring: tp.Optional[str] = None) -> Predicate:
    def operation_v(self) -> Predicate:
        def operate(v):
            return operation(self.operation(v))

        return PredicateClass(operate)

    if docstring:
        operation_v.__doc__ = docstring

    return operation_v


def _has_keys(a: tp.Container, keys) -> bool:
    for key in keys:
        if key not in a:
            return False
    return True


def _one_of(a, values: tp.Container) -> bool:
    return a in values


class PredicateClass:
    """
    A shorthand to create lambdas using such statements, for example:

    >>> add_two = x + 2
    >>> assert add_two(2) == 4
    """
    __slots__ = ('operation',)

    def __init__(self, operation: tp.Callable[[tp.Any], tp.Any] = _nop):
        self.operation = operation

    str = make_operation_single_arg(str, 'Call str() on predicate')
    int = make_operation_single_arg(int, 'Call int() on predicate')
    float = make_operation_single_arg(float, 'Call float() on predicate')
    false = make_operation_single_arg(lambda y: not y, 'Return a predicate checking whether '
                                                       'value is False')

    def __call__(self, *args) -> bool:
        if len(args) == 0:
            return PredicateClass(lambda y: self.operation(y)())
        else:
            return self.operation(args[0])

    def has_keys(self, *keys) -> Predicate:
        """
        Return a predicate checking whether this value has provided keys
        """
        return make_operation_two_args(_has_keys)(self, keys)

    def one_of(self, *values) -> Predicate:
        """
        Return a predicate checking if x is amongst values
        """
        return make_operation_two_args(_one_of)(self, values)

    def has_p(self, predicate: 'PredicateClass') -> Predicate:
        """
        An old name for has().

        It's deprecated. Use has() instead

        .. deprecated:: 2.14.22
        """
        warnings.warn('This is deprecated and will be removed in Satella 3.x.'
                      'Please use has() instead', DeprecationWarning)
        return self.has(predicate)

    def type(self) -> tp.Type:
        """
        Return a predicate returning the type of it's argument
        """

        def type_of(v):
            return type(self.operation(v))

        return PredicateClass(type_of)

    def is_instance(self, *args):
        """
        Check if given value is one of instances.

        :param args: will be passed as argument to isinstance
        """

        def is_instance(v):
            return isinstance(self.operation(v), args)

        return PredicateClass(is_instance)

    def identity(self) -> Predicate:
        """
        Spawn another object with the same operation, but different identity.

        Used for constructing dicts keyed by predicates.
        """
        return PredicateClass(self.operation)

    def is_valid_schema(self, schema: tp.Optional[tp.Union[Descriptor, tp.Dict]] = None, **kwargs):
        """
        Check if given value has the correct schema.
        The schema is the same as in
        :py:meth:`~satella.coding.structures.DictObject.is_valid_schema`
        """

        def is_schema_correct(v):
            from satella.coding.structures import DictObject
            return DictObject(self.operation(v)).is_valid_schema(schema, **kwargs)

        return PredicateClass(is_schema_correct)

    def has(self, predicate: 'PredicateClass') -> Predicate:
        """
        Check if any element of the current value (which must be an iterable)
        returns True when applied to predicate

        :param predicate: predicate that has to return True for at least one of this predicate's
            values
        """

        def op(v):
            for e in self.operation(v):
                if predicate(e):
                    return True
            return False

        return PredicateClass(op)

    inside = make_operation_two_args(operator.contains,
                                     'Return a predicate checking if x is inside value')

    instanceof = make_operation_two_args(isinstance,
                                         'Return a predicate checking whether this value '
                                         'is an instance of instance')

    length = make_operation_single_arg(len, 'Return a predicate returning length of it''s argument')

    __contains__ = make_operation_two_args(operator.contains)
    __getattr__ = make_operation_two_args(getattr)
    __getitem__ = make_operation_two_args(operator.getitem)
    __eq__ = make_operation_two_args(operator.eq)
    __ne__ = make_operation_two_args(operator.ne)
    __lt__ = make_operation_two_args(operator.lt)
    __gt__ = make_operation_two_args(operator.gt)
    __le__ = make_operation_two_args(operator.le)
    __ge__ = make_operation_two_args(operator.ge)
    __add__ = make_operation_two_args(operator.add)
    __sub__ = make_operation_two_args(operator.sub)
    __mul__ = make_operation_two_args(operator.mul)
    __matmul__ = make_operation_two_args(operator.matmul)
    __and__ = make_operation_two_args(operator.and_)
    __or__ = make_operation_two_args(operator.or_)
    __rshift__ = make_operation_two_args(operator.rshift)
    __lshift__ = make_operation_two_args(operator.lshift)
    __xor__ = make_operation_two_args(operator.xor)
    __truediv__ = make_operation_two_args(operator.__truediv__)
    __floordiv__ = make_operation_two_args(operator.floordiv)
    __mod__ = make_operation_two_args(operator.mod)
    __pow__ = make_operation_two_args(operator.pow)
    __radd__ = make_operation_two_args(operator.add, swap_order=True)
    __rsub__ = make_operation_two_args(operator.sub, swap_order=True)
    __rmul__ = make_operation_two_args(operator.mul, swap_order=True)
    __rmatmul__ = make_operation_two_args(operator.matmul, swap_order=True)
    __rand__ = make_operation_two_args(operator.and_, swap_order=True)
    __ror__ = make_operation_two_args(operator.or_, swap_order=True)
    __rrshift__ = make_operation_two_args(operator.rshift, swap_order=True)
    __rlshift__ = make_operation_two_args(operator.lshift, swap_order=True)
    __rxor__ = make_operation_two_args(operator.xor, swap_order=True)
    __rtruediv__ = make_operation_two_args(operator.__truediv__, swap_order=True)
    __rfloordiv__ = make_operation_two_args(operator.floordiv, swap_order=True)
    __rmod__ = make_operation_two_args(operator.mod, swap_order=True)
    __rpow__ = make_operation_two_args(operator.pow, swap_order=True)
    __neg__ = make_operation_single_arg(operator.neg)
    __invert__ = make_operation_single_arg(operator.invert)
    __abs__ = make_operation_single_arg(abs)

    def __hash__(self) -> int:
        return hash(id(self))


x = PredicateClass()


def build_structure(struct: tp.Union[tuple, list, dict],
                    argument,
                    final_operator=lambda y: y,
                    nested_call=False) -> tp.Union[tuple, list, dict]:
    """
    Given a structure (tuple, list, dict) that contains x's as some of the elements,
    build such a structure corresponding to given that all x's are replaced
    by result of their calculation on argument.

    Just note that if you're constructing dictionaries, use the .identity() method of predicate,
    to randomize it's identity.

    :param struct: structure to build
    :param argument: argument
    :param final_operator: an operator to call on the result
    :param nested_call: internal, don't use
    :return: analogous structure
    """
    if not nested_call:
        v = build_structure(struct, argument, None, True)
        return final_operator(v)

    from satella.coding.structures import HashableWrapper
    if isinstance(struct, tp.MutableMapping):
        new_dict = {}
        for key, value in struct.items():
            key = build_structure(key, argument, None, True)
            value = build_structure(value, argument, None, True)
            new_dict[key] = value
            return new_dict
    elif isinstance(struct, tp.Sequence):
        new_seq = []
        for elem in struct:
            if isinstance(elem, PredicateClass):
                elem = elem(argument)
            else:
                elem = build_structure(elem, argument, None, True)
            new_seq.append(elem)
        return struct.__class__(new_seq)
    elif isinstance(struct, HashableWrapper):
        obj = getattr(struct, '_Proxy__obj')
        return build_structure(obj, argument, None, True)
    elif isinstance(struct, PredicateClass):
        return struct(argument)
    else:
        return struct
