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


T = tp.TypeVar('T')


def take_n(iterator: tp.Iterable[T], n: int, skip: int = 0) -> tp.List[T]:
    """
    Take (first) n elements of an iterator, or the entire iterator, whichever comes first

    :param iterator: iterator to take from
    :param n: amount of elements to take
    :param skip: elements from the start to skip
    :return: list of length n (or shorter)
    """
    iterator = iter(iterator)
    for i in range(skip):
        next(iterator)

    output = []
    for i in range(n):
        try:
            output.append(next(iterator))
        except StopIteration:
            return output
    return output
