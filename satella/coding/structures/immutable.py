__all__ = ['Immutable']


class ImmutableMetaType(type):
    def __call__(cls, *args, **kwargs):
        p = type.__call__(cls, *args, **kwargs)
        p.__class__ = LockedImmutable
        return p


class Immutable(metaclass=ImmutableMetaType):
    """
    A mix-in to make your classes immutable.

    You can assign normally using your constructor.

    >>> class Test(Immutable):
    >>>     def __init__(self):
    >>>         self.attribute = 'value'
    """


class LockedImmutable(Immutable):

    __doc__ = Immutable.__doc__

    # Following make this class immutable
    def __setattr__(self, attr, value):
        raise TypeError('%s does not support attribute assignment' % (self.__class__.__qualname__,))

    def __delattr__(self, attr):
        raise TypeError('%s does not support attribute deletion' % (self.__class__.__qualname__,))
