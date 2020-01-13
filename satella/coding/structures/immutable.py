class Immutable:
    """
    A mix-in to make your classes immutable.

    Please assign values this way in the constructor:

    >>> super().__setattr__('attribute', value)
    """

    # Following make this class immutable
    def __setattr__(self, attr, value):
        raise TypeError('%s does not support attribute assignment' % (self.__class__.__qualname__, ))

    def __delattr__(self, attr):
        raise TypeError('%s does not support attribute deletion' % (self.__class__.__qualname__, ))
