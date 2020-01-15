import logging
import typing as tp

logger = logging.getLogger(__name__)

from satella.imports import import_from

__all__ = []


def do_import():
    logger.warning(repr(__path__))
    logger.warning(repr(__name__))
    import_from(__path__, __name__, __all__, locals(), recursive=True, fail_on_attributerror=False, add_all=True)
