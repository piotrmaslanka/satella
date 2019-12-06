import logging
import os
import typing as tp
import sys

from satella.coding import rethrow_as
from satella.exceptions import ConfigurationError
from .base import BaseSource
from .format import JSONSource

logger = logging.getLogger(__name__)

__all__ = [
    'EnvVarsSource', 'EnvironmentSource',
]


class EnvironmentSource(BaseSource):
    """
    This just returns a dictionary of { env_name => that env's value }
    """

    def __init__(self, env_name: str, config_name: tp.Optional[str] = None, cast_to=lambda v: v):
        super(EnvironmentSource, self).__init__()
        self.env_name = env_name
        self.config_name = config_name or env_name
        self.cast_to = cast_to

    @rethrow_as((ValueError, TypeError, KeyError), ConfigurationError)
    def provide(self) -> dict:
        v = self.cast_to(os.environ[self.env_name])

        return {self.config_name: v}


class EnvVarsSource(JSONSource):
    def __init__(self, env_name: str):
        super(EnvVarsSource, self).__init__('',
                                            encoding=sys.getfilesystemencoding())
        self.env_name = env_name

    @rethrow_as(KeyError, ConfigurationError)
    def provide(self) -> dict:
        self.root = os.environ[self.env_name]
        return super(EnvVarsSource, self).provide()
