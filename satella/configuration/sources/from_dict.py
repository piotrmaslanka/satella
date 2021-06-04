import copy
import importlib
import warnings

from satella.coding.recast_exceptions import rethrow_as
from satella.configuration import sources
from satella.configuration.sources.base import BaseSource
from satella.exceptions import ConfigurationError, ConfigurationMisconfiguredError

__all__ = [
    'load_source_from_dict',
    'load_source_from_list'
]


def handle_import(dct: dict):
    def convert(v):
        if 'cast_before' in dct:
            v = EXTRA_TYPES[dct['cast_before']['type']](dct['cast_before'])(v)

        return getattr(importlib.import_module(dct['module']), dct['attribute'])(v)

    return convert


EXTRA_TYPES = {
    'binary': lambda dct: dct['value'].encode(dct.get('encoding', 'ascii')),
    'lambda': lambda dct: eval('lambda x: ' + dct['operation'], globals(),
                               locals()),
    'import': handle_import,
}


@rethrow_as(Exception, ConfigurationError)
def load_source_from_dict(dct: dict) -> BaseSource:
    """
    obj has a form of

    {
        "type": "BaseSource",
        "args": []  # optional
        ... kwargs
    }

    :raises ConfigurationError: upon failure to instantiate
    """
    dct = copy.copy(dct)
    type_ = dct.pop('type')  # type: str
    if 'arg' in dct:
        args = dct.pop('arg'),
    else:
        args = dct.pop('args', [])  # type: tp.List

    optional = dct.pop('optional', False)  # type: bool

    def to_arg(arg):
        if isinstance(arg, dict) and 'type' in arg:
            a_type = arg['type']
            if a_type in EXTRA_TYPES:
                return EXTRA_TYPES[a_type](arg)
            elif a_type in sources.__dict__:
                return load_source_from_dict(arg)
            else:
                warnings.warn(
                    'Caught %s attempting to parse a dict with type, returning original value' % (
                        e,), UserWarning)
                return arg
        else:
            return arg

    args = map(to_arg, args)
    kwargs = {k: to_arg(v) for k, v in dct.items()}

    try:
        s = sources.__dict__[type_](*args, **kwargs)
    except KeyError as e:
        raise ConfigurationMisconfiguredError('unknown type %s' % (type_,))

    if optional:
        s = sources.OptionalSource(s)
    return s


def load_source_from_list(obj: list) -> 'sources.MergingSource':
    """
    Builds a MergingSource from dict-ed objects
    """
    return sources.MergingSource(*map(load_source_from_dict, obj))
