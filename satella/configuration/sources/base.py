__all__ = [
    'BaseSource',
    'StaticSource'
]


class BaseSource(object):
    """Base class for all configuration sources"""

    def provide(self) -> dict:
        """
        Return your configuration, as a dict

        :raise ConfigurationError: on invalid configuration
        """
        return {}


class StaticSource(BaseSource):
    """
    A static piece of configuration. Returns exactly what is passed
    """

    def __init__(self, config: dict):
        self.config = config

    def provide(self) -> dict:
        return self.config
