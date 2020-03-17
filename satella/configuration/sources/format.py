import binascii
import codecs
import json
import typing as tb

from satella.coding.recast_exceptions import rethrow_as
from satella.exceptions import ConfigurationError
from .base import BaseSource

__all__ = [
    'FormatSource', 'FORMAT_SOURCES'
]

FORMAT_SOURCES = []  # sources capable of parsing a text format


def register_format_source(source):
    source_name = source.__name__
    __all__.append(source_name)
    FORMAT_SOURCES.append(source_name)

    return source


def _override_me(key):
    raise NotImplementedError('override me')


class FormatSource(BaseSource):
    __slots__ = ('root', 'encoding')

    TRANSFORM = _override_me
    BASE_EXCEPTIONS = [TypeError, UnicodeDecodeError, ValueError,
                       binascii.Error, LookupError]
    EXTRA_EXCEPTIONS = []

    def __init__(self, root: tb.Union[bytes, str], encoding: str = 'utf-8'):
        """
        :param root: content
        :type root: if bytes, will be decoded with given encoding'
        """
        super().__init__()
        self.root = root                # type: BaseSource
        self.encoding = encoding        # type: str

    def provide(self) -> dict:
        cls = self.__class__

        with rethrow_as(tuple(cls.BASE_EXCEPTIONS + cls.EXTRA_EXCEPTIONS),
                        ConfigurationError):
            if isinstance(self.root, bytes):
                self.root = codecs.decode(self.root, self.encoding)
                if isinstance(self.root, bytes):  # probably base64 encoded
                    self.root = self.root.decode('utf-8')

            ret_val = cls.TRANSFORM(self.root)
            if not isinstance(ret_val, dict):
                raise ConfigurationError(
                    'provider was unable to generate a text volume')
            else:
                return ret_val


@register_format_source
class JSONSource(FormatSource):
    """
    Loads JSON strings
    """
    TRANSFORM = json.loads
    EXTRA_EXCEPTIONS = [json.JSONDecodeError]


try:
    import yaml
except ImportError:
    pass
else:
    @register_format_source
    class YAMLSource(FormatSource):
        """
        Loads YAML strings
        """
        EXTRA_EXCEPTIONS = [yaml.YAMLError]
        TRANSFORM = lambda data: yaml.load(data, Loader=yaml.Loader)

try:
    import toml
except ImportError:
    pass
else:
    @register_format_source
    class TOMLSource(FormatSource):
        """
        Loads TOML strings
        """
        EXTRA_EXCEPTIONS = [toml.TomlDecodeError]
        TRANSFORM = toml.loads
