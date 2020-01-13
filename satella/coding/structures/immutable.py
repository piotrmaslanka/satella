class ImmutableMetaType(type):
    def __call__(cls, *args, **kwargs):
        p = type.__call__(cls, *args, **kwargs)
        p._Immutable__lock_for_writes()
        return p


class Immutable(metaclass=ImmutableMetaType):
    """
    A mix-in to make your classes immutable.

    You can assign normally using your constructor.

    >>> class Test(Immutable):
    >>>     def __init__(self):
    >>>         self.attribute = 'value'
    """

    __locked_for_writes: bool = False

    def __lock_for_writes(self):
        self.__locked_for_writes = True

    # Following make this class immutable
    def __setattr__(self, attr, value):
        if not self.__locked_for_writes:
            super().__setattr__(attr, value)
        else:
            raise TypeError('%s does not support attribute assignment' % (self.__class__.__qualname__, ))

    def __delattr__(self, attr):
        if not self.__locked_for_writes:
            super().__setattr__(attr, value)
        else:
            raise TypeError('%s does not support attribute deletion' % (self.__class__.__qualname__, ))
