import logging
import typing as tp

logger = logging.getLogger(__name__)


def infinite_counter(start_at: int = 0, step: int = 1) -> tp.Generator[int, None, None]:
    """
    Infinite counter, starting at start_at

    :param start_at: value at which to start counting. It will be yielded as first
    :param step: step by which to progress the counter
    """

    i = start_at
    while True:
        yield i
        i += step
