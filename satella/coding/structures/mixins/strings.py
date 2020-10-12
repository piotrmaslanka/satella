from abc import ABCMeta, abstractmethod


class StrEqHashableMixin(metaclass=ABCMeta):
    """
    A mix-in that outfits your class with an __eq__ and __hash__ operator that take
    their values from __str__ representation of your class.
    """
    __slots__ = ()

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))

    @abstractmethod
    def __str__(self) -> str:
        pass


class ReprableMixin:
    """
    A sane __repr__ default.

    This takes the values for the __repr__ from repr'ing list of fields defined as
    class property _REPR_FIELDS.

    Set an optional class property of _REPR_FULL_CLASSNAME for __repr__ to output the repr
    alongside the module name.

    Example:

    >>> class Test(ReprableMixin):
    >>>     _REPR_FIELDS = ('v', )
    >>>     def __init__(self, v, **kwargs):
    >>>         self.v = v
    >>>
    >>> assert repr(Test(2)) == "Test(2)"
    >>> assert repr(Test('2') == "Test('2')")
    """
    __slots__ = ()
    _REPR_FIELDS = ()

    def __repr__(self):
        fragments = []
        if getattr(self, '_REPR_FULL_CLASSNAME', False):
            fragments = ['%s%s' % ((self.__class__.__module__ + '.')
                                   if self.__class__.__module__ != 'builtins' else '',
                                   self.__class__.__qualname__)]
        if not fragments:
            fragments = [self.__class__.__name__]
        fragments.append('(')
        arguments = []
        for field_name in self._REPR_FIELDS:
            arguments.append(repr(getattr(self, field_name)))
        fragments.append(', '.join(arguments))
        fragments.append(')')
        return ''.join(fragments)
