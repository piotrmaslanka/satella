__all__ = [
    'BaseSource'
]


class BaseSource(object):
    """Base class for all configuration sources"""

    def provide(self) -> dict:
        """
        Return your configuration, as a dict

        :raise ConfigurationError: on invalid configuration
        """
        return {}
