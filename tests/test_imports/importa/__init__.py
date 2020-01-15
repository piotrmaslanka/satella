import logging

logger = logging.getLogger(__name__)

from satella.imports import import_from

__all__ = []


def do_import():
    import_from(__path__, __name__, __all__, locals(), recursive=True, fail_on_attributerror=False,
                create_all=True)
