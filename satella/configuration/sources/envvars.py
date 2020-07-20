import os
import sys
import typing as tp
import warnings

from satella.coding.recast_exceptions import rethrow_as
from satella.exceptions import ConfigurationError
from .base import BaseSource
from .format import JSONSource

__all__ = [
    'EnvVarsSource', 'EnvironmentSource',
]


class EnvironmentSource(BaseSource):
    """
    This just returns a dictionary of { env_name => that env's value }

    :param env_name: name of the environment variable to check for
    :param config_name: name of the env_name in the dictionary to return
    :param cast_to: callable that converts a string to whatever form is desired.
        Note that this is **deprecated**. Use schema instead to cast to desired typing.
    """
    __slots__ = ('env_name', 'config_name', 'cast_to')

    def __init__(self, env_name: str, config_name: tp.Optional[str] = None, cast_to=None):
        super(EnvironmentSource, self).__init__()
        self.env_name = env_name  # type: str
        self.config_name = config_name or env_name  # type: str
        if cast_to is not None:
            warnings.warn(
                'Use .schema module to cast values to target type. '
                'This module is only concerned with loading the configuration.'
                'This feature will be removed in Satella 3.0', DeprecationWarning)
            self.cast_to = cast_to  # type: tp.Callable[[tp.Any], tp.Any]
        else:
            self.cast_to = lambda x: x

    @rethrow_as((ValueError, TypeError, KeyError), ConfigurationError)
    def provide(self) -> dict:
        v = self.cast_to(os.environ[self.env_name])

        return {self.config_name: v}


class EnvVarsSource(JSONSource):
    """
    Return a dictionary that is the JSON encoded within a particular environment variable
    """
    __slots__ = ('env_name',)

    def __init__(self, env_name: str):
        super(EnvVarsSource, self).__init__('',
                                            encoding=sys.getfilesystemencoding())
        self.env_name = env_name  # type: str

    @rethrow_as(KeyError, ConfigurationError)
    def provide(self) -> dict:
        self.root = os.environ[self.env_name]
        return super(EnvVarsSource, self).provide()
