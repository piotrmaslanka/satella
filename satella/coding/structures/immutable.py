from abc import ABCMeta

__all__ = ['Immutable', 'frozendict']


class ImmutableMetaType(ABCMeta):
    def __call__(cls, *args, **kwargs):
        p = type.__call__(cls, *args, **kwargs)
        p.__dict__['_Immutable__locked_for_writes'] = True
        return p


class Immutable(metaclass=ImmutableMetaType):
    """
    A mix-in to make your classes immutable.

    You can assign normally using your constructor.

    >>> class Test(Immutable):
    >>>     def __init__(self):
    >>>         self.attribute = 'value'
    """

    __locked_for_writes = False

    # Following make this class immutable
    def __setattr__(self, attr, value):
        if self.__locked_for_writes:
            raise TypeError(
                '%s does not support attribute assignment' % (self.__class__.__qualname__,))
        else:
            super().__setattr__(attr, value)

    def __delattr__(self, attr):
        if self.__locked_for_writes:
            raise TypeError(
                '%s does not support attribute deletion' % (self.__class__.__qualname__,))
        else:
            super().__delattr__(attr)


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
