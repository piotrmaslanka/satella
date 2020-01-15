import logging

logger = logging.getLogger(__name__)

__all__ = ['add', 'would_have_failed']


def add(a: float, b: float) -> float:
    return a + b
