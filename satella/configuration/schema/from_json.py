import typing as tp

from satella.exceptions import ConfigurationSchemaError
from satella.imports import import_class
from .base import Descriptor
from .registry import BASE_LOOKUP_TABLE, PLAIN_ENTRIES
from .structs import create_key, Dict


def _get_descriptor_for_str(key: str, value: str) -> Descriptor:
    try:
        if value in PLAIN_ENTRIES:
            return create_key(BASE_LOOKUP_TABLE[value](),
                              key, False, None)
    except KeyError:
        raise ConfigurationSchemaError('Unknown descriptor type %s' % (value,))


def _get_descriptor_for_dict(key: str, value: dict) -> Descriptor:
    if 'type' not in value:
        return create_key(descriptor_from_dict(value),
                          key, False, None)
    else:
        args = ()
        type_ = value['type']
        if type_ == 'list':
            of = _get_descriptor_for('', value.get('of', ''))
            args = (of,)
        elif type_ == 'caster':
            cast_to = value.get('cast_to')
            dict_to_look_in = globals().copy()
            if not isinstance(__builtins__, dict):
                dict_to_look_in.update(__builtins__.__dict__)
            else:
                dict_to_look_in.update(__builtins__)
            dict_to_look_in.update(locals())
            if cast_to in dict_to_look_in:
                y = dict_to_look_in[cast_to]
            else:
                y = import_class(cast_to)

            if 'expr' in value:
                dict_ = globals().copy()
                dict_.update(locals())
                dict_['y'] = y
                args = eval('lambda x: ' + value['expr'], dict_),
            else:
                args = y,
        elif type_ == 'file_contents':
            args = value.get('encoding', None), value.get('strip_afterwards', False)
        elif type_ == 'union':
            args = [_get_descriptor_for('', x) for x in value.get('of', [])]
        optional, default = False, None
        if 'default' in value:
            optional = True
            default = value['default']
        optional = value.get('optional', optional)
        descriptor = BASE_LOOKUP_TABLE[type_](*args)
        return create_key(descriptor, key, optional, default)


def _get_descriptor_for(key: str, value: tp.Any) -> Descriptor:
    if value == '':
        return Descriptor()
    elif isinstance(value, str):
        return _get_descriptor_for_str(key, value)
    elif isinstance(value, dict):
        return _get_descriptor_for_dict(key, value)
    elif isinstance(value, type):
        return _get_descriptor_for(key, value.__qualname__)
    else:
        raise ConfigurationSchemaError('invalid schema, unrecognized config object %s' % (value,))


def descriptor_from_dict(dct: dict) -> Descriptor:
    """
    Giving a Python dictionary-defined schema of the configuration, return a Descriptor-based one

    :param dct: something like
    {
        "a": "int",
        "b": "str",
        "c": {
            "type": "int"
            "optional": True,
            "default": 5
        },
        "d": {
            "a": "int",
            "b": "str"
        }
    }

    although you can pass "int", "float" and "str" without enclosing quotes, that will work too

    :return: a Descriptor-based schema
    """
    fields = []

    for key, value in dct.items():
        descriptor = _get_descriptor_for(key, value)
        fields.append(descriptor)

    return Dict(fields)
