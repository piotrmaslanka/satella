import logging
import typing as tp

logger = logging.getLogger(__name__)


class DictObject(dict):
    def __getattr__(self, item: str) -> tp.Any:
        try:
            return self[item]
        except KeyError as e:
            raise AttributeError(repr(e))

    def __setattr__(self, key: str, value: tp.Any) -> None:
        self[key] = value

    def __delattr__(self, key: str) -> None:
        try:
            del self[key]
        except KeyError as e:
            raise AttributeError(repr(e))
