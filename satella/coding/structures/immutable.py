from abc import ABCMeta


class ImmutableMetaType(ABCMeta):
    def __call__(cls, *args, **kwargs):
        p = type.__call__(cls, *args, **kwargs)
        setattr(p, '_Immutable__locked_for_writes', True)
        return p


class Immutable(metaclass=ImmutableMetaType):
    """
    A mix-in to make your classes immutable.

    You can assign normally using your constructor.

    >>> class Test(Immutable):
    >>>     def __init__(self):
    >>>         self.attribute = 'value'
    """

    __slots__ = ('__locked_for_writes',)

    # Following make this class immutable
    def __setattr__(self, attr, value):
        if attr == '_Immutable__locked_for_writes':
            return super().__setattr__(attr, value)

        try:
            if self.__locked_for_writes:
                raise TypeError(
                    '%s does not support attribute assignment' % (self.__class__.__qualname__,))
            else:
                super().__setattr__(attr, value)
        except AttributeError:
            super().__setattr__(attr, value)

    def __delattr__(self, attr):
        try:
            if self.__locked_for_writes:
                raise TypeError(
                    '%s does not support attribute deletion' % (self.__class__.__qualname__,))
            else:
                super().__delattr__(attr)
        except AttributeError:
            super().__delattr__(attr)


class NotEqualToAnything:
    """
    A class that defines __eq__ and __ne__ to be always False and True respectively

    When exploiting this class please make sure that it gets to be the first
    operand in the comparison, so that it's __eq__ and __ne__ gets called!
    """

    def __eq__(self, other) -> bool:
        return False

    def __next__(self, other) -> bool:
        return True


NOT_EQUAL_TO_ANYTHING = NotEqualToAnything()


class frozendict(dict):
    """
    A hashable dict with express forbid to change it's values
    Both keys and values must be hashable in order for this dict to be hashable.
    """

    def __setitem__(self, key, value):
        raise TypeError('Cannot update a frozen dict!')

    def update(self, *args, **kwargs):
        raise TypeError('Cannot update a frozen dict!')

    def __hash__(self):
        o = 0
        for key, value in self.items():
            o = o ^ hash(key) ^ hash(value)
        return o
