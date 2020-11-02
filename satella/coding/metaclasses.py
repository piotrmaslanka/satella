import inspect

from .decorators import wraps
from .sequences.iterators import walk
from .typing import Predicate

"""
Taken from http://code.activestate.com/recipes/204197-solving-the-metaclass-conflict/ and slightly
modified
"""
from abc import ABCMeta
import typing as tp


def _extract_bases(cls):
    if isinstance(cls, (tuple, list)):
        return cls
    else:
        return [v_base for v_base in cls.__bases__ if v_base is not object]


def CopyDocsFrom(target_cls: tp.Type):
    """
    A metaclass to copy documentation from some other class for respective methods.

    >>> class Source:
    >>>     def test(self):
    >>>        'docstring'
    >>> class Target(metaclass=CopyDocsFrom(Source)):
    >>>     def test(self):
    >>>         ...
    >>> assert Target.test.__doc__ == Source.test.__doc__

    :param target_cls: class from which to copy the docs
    """

    def inner(name, bases, dictionary):
        if '__doc__' not in dictionary:
            if hasattr(target_cls, '__doc__'):
                if target_cls.__doc__:
                    dictionary['__doc__'] = target_cls.__doc__

        for key, value in dictionary.items():
            if not value.__doc__ and callable(value):
                if hasattr(target_cls, key):
                    if getattr(target_cls, key).__doc__:
                        value.__doc__ = getattr(target_cls, key).__doc__
                        dictionary[key] = value
                        break

        return type(name, bases, dictionary)

    return inner


def DocsFromParent(name: str, bases: tp.Tuple[type], dictionary: dict) -> tp.Type:
    """
    A metaclass that fetches missing docstring's for methods from the classes' bases,
    looked up BFS. This will fetch the class's docstring itself, if available and not
    present in the child.

    >>> class Father:
    >>>     def test(self):
    >>>         '''my docstring'''

    >>> class Child(Father, metaclass=DocsFromParent):
    >>>     def test(self):
    >>>         ...
    >>> assert Child.test.__doc__ == 'my docstring'
    """
    if '__doc__' not in dictionary:
        for base in walk(bases, _extract_bases, deep_first=False):
            if hasattr(base, '__doc__'):
                if base.__doc__:
                    dictionary['__doc__'] = base.__doc__
                    break

    for key, value in dictionary.items():
        if not value.__doc__ and callable(value):
            for base in walk(bases, _extract_bases, deep_first=False):
                if hasattr(base, key):
                    if getattr(base, key).__doc__:
                        value.__doc__ = getattr(base, key).__doc__
                        dictionary[key] = value
                        break
    return type(name, bases, dictionary)


def skip_redundant(iterable, skip_set=None):
    """Redundant items are repeated items or items in the original skip_set."""
    if skip_set is None:
        skip_set = set()

    for item in iterable:
        if item not in skip_set:
            skip_set.add(item)
            yield item


def remove_redundant(metaclasses):
    skip_set = {type}
    for meta in metaclasses:  # determines the metaclasses to be skipped
        skip_set.update(inspect.getmro(meta)[1:])
    return tuple(skip_redundant(metaclasses, skip_set))


memoized_metaclasses_map = {}


def get_noconflict_metaclass(bases,
                             left_metas,
                             right_metas) -> tp.Callable[[str, tuple, dict], tp.Type]:
    """Not intended to be used outside of this module, unless you know
    what you are doing."""
    # make tuple of needed metaclasses in specified priority order
    metas = left_metas + tuple(map(type, bases)) + right_metas
    needed_metas = remove_redundant(metas)

    # return existing conflict-solving meta, if any
    if needed_metas in memoized_metaclasses_map:
        return memoized_metaclasses_map[needed_metas]
    # nope: compute, memoize and return needed conflict-solving meta
    elif not needed_metas:  # wee, a trivial case, happy us
        meta = type
    elif len(needed_metas) == 1:  # another trivial case
        meta = needed_metas[0]
    # check for recursion, can happen i.e. for Zope ExtensionClasses
    elif needed_metas == bases:
        raise TypeError("Incompatible root meta-types", needed_metas)
    else:  # gotta work ...
        meta_name = '_' + ''.join([m.__name__ for m in needed_metas])
        meta = metaclass_maker_f()(meta_name, needed_metas, {})
    memoized_metaclasses_map[needed_metas] = meta
    return meta


def metaclass_maker_f(left_metas=(), right_metas=()):
    def make_class(name: str, bases: tuple, a_dict: dict) -> tp.Type:
        metaclass = get_noconflict_metaclass(bases, left_metas, right_metas)
        return metaclass(name, bases, a_dict)

    return make_class


def metaclass_maker(name: str, bases: tuple, a_dict: dict) -> tp.Type:
    """
    Automatically construct a compatible meta-class like interface. Use like:

    >>> class C(A, B, metaclass=metaclass_maker):
    >>>     pass
    """
    metaclass = get_noconflict_metaclass(bases, (), ())
    return metaclass(name, bases, a_dict)


GetterDefinition = tp.Callable[[object], tp.Any]
SetterDefinition = tp.Callable[[object, tp.Any], None]
DeleterDefinition = tp.Callable[[object], None]


def wrap_property(getter: tp.Callable[[GetterDefinition], GetterDefinition] = lambda x: x,
                  setter: tp.Callable[[SetterDefinition], SetterDefinition] = lambda x: x,
                  deleter: tp.Callable[[DeleterDefinition], DeleterDefinition] = lambda x: x):
    """
    Construct a property wrapper.

    This will return a function, that if given a property, will wrap it's getter, setter and
    deleter with provided functions.

    Getter, setter and deleter are extracted from fget, fset and fdel, so only native properties,
    please, not descriptor-objects.

    :param getter: callable that accepts a callable(instance) -> value, and returns the same.
        Getter will be wrapped by this
    :param setter: callable that accepts a callable(instance, value) and returns the same.
        Setter will be wrapped by this
    :param deleter: callable that accepts a callable(instance), and returns the same.
        Deleter will be wrapped by this
    """

    def inner(prop):
        return wraps(prop)(property(getter(prop.fget), setter(prop.fset), deleter(prop.fdel)))

    return inner


def wrap_with(callables: tp.Callable[[tp.Callable], tp.Callable] = lambda x: x,
              properties: tp.Callable[[property], property] = lambda x: x,
              selector_callables: Predicate[tp.Callable] = lambda clb: True,
              selector_properties: Predicate[property] = lambda clb: True):
    """
    A metaclass that wraps all elements discovered in this class with something

    Example:

    >>> def make_double(fun):
    >>>     return lambda self, x: fun(x)*2
    >>> class Doubles(metaclass=wrap_all_methods_with(make_double)):
    >>>     def return_four(self, x):
    >>>         return 2
    >>> assert Doubles().return_four(4) == 4

    Note that every callable that appears in the class namespace, ie. object that has __call__
    will be considered for wrapping.

    This is compatible with the abc.ABCMeta metaclass

    :param callables: function to wrap all callables with given class with
    :param properties: function to wrap all properties with given class with
    :param selector_callables: additional criterion to be ran on given callable before deciding
        to wrap it. It must return True for wrapping to proceed.
    :param selector_properties: additional criterion to be ran on given property before deciding
        to wrap it. It must return True for wrapping to proceed.
    """

    @wraps(ABCMeta)
    def WrapAllMethodsWithMetaclass(name, bases, dct):
        new_dct = {}
        for key, value in dct.items():
            if not hasattr(value, '_dont_wrap'):
                if callable(value) and selector_callables(value):
                    value = callables(value)
                elif isinstance(value, property) and selector_properties(value):
                    value = properties(value)
            new_dct[key] = value
        return ABCMeta(name, bases, new_dct)

    return WrapAllMethodsWithMetaclass


def dont_wrap(fun):
    """A special decorator to save given class member from being mulched by wrap_with"""
    fun._dont_wrap = True
    return fun
