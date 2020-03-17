import copy
import importlib

from satella.coding.recast_exceptions import rethrow_as
from satella.coding.decorators import for_argument
from satella.configuration import sources
from satella.configuration.sources.base import BaseSource
from satella.exceptions import ConfigurationError

"""
If a dict has a field "type" then it will be treated specially:

* "binary" - it is a binary value of "value" to be encoded with "encoding" (default ascii)
* "lambda" - it allows expressing the simplest filters there can be
  name of a source class - it will be instantated with arguments "args".
  rest keys will be kwargs.
* "import" it will import "attribute" from module "module" and call it with this value,
  optionally preprocessing it with "cast_before"
                             
Special key is "optional" to be bool - if so, the source will be decorated as optional
                                                          
See the unit test for more in-depth knowledge
"""

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
@for_argument(copy.copy)  # since we are modyfing that dict
def load_source_from_dict(dct: dict) -> BaseSource:
    """
    dct has a form of

    {
        "type": "BaseSource",
        "args": []  # optional
        ... kwargs
    }

    :raises ConfigurationError: upon failure to instantiate
    """
    type_ = dct.pop('type')                     # type: str
    args = dct.pop('args', [])                  # type: tp.List
    optional = dct.pop('optional', False)       # type: bool

    def argify(arg):
        if isinstance(arg, dict) and 'type' in arg:
            atype = arg['type']
            if atype in EXTRA_TYPES:
                return EXTRA_TYPES[atype](arg)
            elif atype in sources.__dict__:
                return load_source_from_dict(arg)
            else:
                raise ValueError(
                    'unrecognized argument type %s' % (arg['type'],))
        else:
            return arg

    args = map(argify, args)
    kwargs = {k: argify(v) for k, v in dct.items()}

    s = sources.__dict__[type_](*args, **kwargs)

    if optional:
        s = sources.OptionalSource(s)
    return s


def load_source_from_list(obj: list) -> BaseSource:
    """
    Builds a MergingSource from dict-ed objects
    """
    return sources.MergingSource(*map(load_source_from_dict, obj))
