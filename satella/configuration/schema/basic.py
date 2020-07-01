import re
import typing as tp

from satella.exceptions import ConfigurationValidationError
from .base import Descriptor, ConfigDictValue
from .registry import register_custom_descriptor


@staticmethod
def _make_boolean(v: tp.Any) -> bool:
    if isinstance(v, str):
        if v.upper() == 'TRUE':
            return True
        elif v.upper() == 'FALSE':
            return False
        else:
            raise ConfigurationValidationError('Unknown value of "%s" posing to be a bool'
                                               % (v,))
    else:
        return bool(v)


@register_custom_descriptor('bool')
class Boolean(Descriptor):
    """
    This value must be a boolean, or be converted to one
    """
    BASIC_MAKER = _make_boolean


@register_custom_descriptor('int')
class Integer(Descriptor):
    """
    This value must be an integer, or be converted to one
    """
    BASIC_MAKER = int


@register_custom_descriptor('float')
class Float(Descriptor):
    """
    This value must be a float, or be converted to one
    """
    BASIC_MAKER = float


@register_custom_descriptor('str')
class String(Descriptor):
    """
    This value must be a string, or be converted to one
    """
    BASIC_MAKER = str


class Regexp(String):
    """
    Base class for declaring regexp-based descriptors. Overload it's attribute REGEXP. Use as
    following:

    >>> class IPv6(Regexp):
    >>>     REGEXP = '(([0-9a-f]{1,4}:)' ...
    """
    __slots__ = ('regexp',)

    REGEXP = r'.*'

    def __init__(self):
        super().__init__()
        if isinstance(self.REGEXP, str):
            self.regexp = re.compile(self.REGEXP)
        else:
            self.regexp = self.REGEXP

    def __call__(self, value: ConfigDictValue) -> str:
        value = super(Regexp, self).__call__(value)

        match = self.regexp.match(value)
        if not match:
            raise ConfigurationValidationError('value does not match %s' % (self.REGEXP.pattern,),
                                               value)

        return match.group(0)

    def __str__(self):
        return 'Regexp(%s)' % (self.REGEXP.pattern,)


@register_custom_descriptor('ipv4')
class IPv4(Regexp):
    """
    This must be a valid IPv4 address (no hostnames allowed)
    """
    REGEXP = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
