import itertools

import typing as tp
import warnings

from ..decorators import for_argument

T, U = tp.TypeVar('T'), tp.TypeVar('U')

IteratorOrIterable = tp.Union[tp.Iterator[T], tp.Iterable[T]]


@for_argument(iter)
def even(sq: IteratorOrIterable) -> tp.Iterator[T]:
    """
    Return only elements with even indices in this iterable (first element will be returned,
    as indices are counted from 0)
    """
    try:
        while True:
            yield next(sq)
            next(sq)
    except StopIteration:
        return


@for_argument(iter)
def odd(sq: IteratorOrIterable) -> tp.Iterator[T]:
    """
    Return only elements with odd indices in this iterable.
    """
    try:
        while True:
            next(sq)
            yield next(sq)
    except StopIteration:
        return


def count(sq: IteratorOrIterable, start: tp.Optional[int] = None, step: int = 1) -> tp.Iterator[int]:
    """
    Return a sequence of integers, for each entry in the sequence with provided step.

    Essentially the same (if step were ignored) as:

    >>> (i for i, x in enumerate(sq, start=start_at))

    :param sq: sequence to enumerate
    :param start: alias for start_at. Prefer it in regards to start_at
    :param step: number to add to internal counter after each element
    :return: an iterator of subsequent integers
    """
    num = start
    for _ in sq:
        yield num
        num += step


def iter_dict_of_list(dct: tp.Dict[T, tp.List[U]]) -> tp.Generator[tp.Tuple[T, U], None, None]:
    """
    Presents a simple way to iterate over a dictionary whose values are lists.

    This will return the dictionary key and each of the value contained in the list attached to
    the key.
    """
    for key, items in dct.items():
        for item in items:
            yield key, item


def infinite_counter(start_at: int = 0, step: int = 1) -> tp.Generator[int, None, None]:
    """
    Infinite counter, starting at start_at

    :param start_at: value at which to start counting. It will be yielded as first
    :param step: step by which to progress the counter
    """
    warnings.warn('This is deprecated, use itertools.count() instead', DeprecationWarning)
    i = start_at
    while True:
        yield i
        i += step


def is_instance(classes: tp.Union[tp.Tuple[type, ...], type]) -> tp.Callable[[object], bool]:
    def inner(object_):
        return isinstance(object_, classes)

    inner.__doc__ = """Return a bool telling if object is of type %s""" % (repr(classes),)
    return inner


def other_sequence_no_longer_than(base_sequence: IteratorOrIterable,
                                  other_sequence: IteratorOrIterable[T]) -> tp.Iterator[T]:
    """
    Return every item in other_sequence, but limit it's p_len to that of base_sequence.

    If other_sequence is shorter than base_sequence, the shorter one will be returned.

    :param base_sequence: sequence whose p_len should be taken
    :param other_sequence: sequence to output values from
    """
    base_sequence, other_sequence = iter(base_sequence), iter(other_sequence)
    while True:
        try:
            next(base_sequence)
            yield next(other_sequence)
        except StopIteration:
            return


def shift(iterable: IteratorOrIterable[T], shift_factor: int) -> tp.Iterator[T]:
    """
    Return this sequence, but shifted by factor elements, so that elements will appear
    sooner by factor.

    Eg:

    >>> assert list(shift([1,2, 3], 1)) == [2, 3, 1]

    However note that this will result in iterators which have negative shift to be readed entirely
    into memory (converted internally to lists). This can be avoided by passing in a Reversible
    iterable.

    :param iterable: iterable to shift
    :param shift_factor: factor by which shift elements.
    :return: shifted sequence
    """

    if shift_factor >= 0:
        iterator = iter(iterable)
        elements = []
        for i in range(shift_factor):
            elements.append(next(iterator))
        return itertools.chain(iterator, elements)
    else:
        if hasattr(iterable, '__reversed__'):
            elements = take_n(reversed(iterable), -shift_factor)
            elements = reversed(elements)
            return other_sequence_no_longer_than(iterable, itertools.chain(elements, iterable))
        else:
            iterator = list(iterable)
            iterator = iterator[shift_factor:] + iterator[:shift_factor]  # shift's already negative
            return iterator


def zip_shifted(*args: tp.Union[IteratorOrIterable[T], tp.Tuple[IteratorOrIterable[T], int]]) -> \
        tp.Iterator[tp.Tuple[T, ...]]:
    """
    Construct an iterator, just like zip but first by cycling it's elements by it's shift factor.
    Elements will be shifted by a certain factor, this means that they will appear earlier.

    Example:

    >>> zip_shifted(([1, 2, 3, 4], 1), ([1, 2, 3, 4], 0)) == [(2, 1), (3, 2), (4, 3), (1, 4)]

    This will work on arbitrary iterators and iterables.

    Shift can be negative, in which case the last elements will appear sooner, eg.

    >>> zip_shifted(([1, 2, 3, 4], -1), ([1, 2, 3, 4], 0)) == [(4, 1), (1, 2), (2, 3), (3, 4)]

    Same memory considerations as :func:`shift` apply.

    The resulting iterator will be as long as the shortest sequence.
    :param args: a tuple with the iterator/iterable and amount of shift. If a non-tuple is given,
        it is assumed that the shift is zero.
    """
    warnings.warn('Use zip(shift(...)) instead!', DeprecationWarning)

    iterators = []  # type: tp.List[tp.Union[tp.Tuple[tp.Iterator[T], tp.List[T]], tp.Iterator[T]]
    for row in args:
        if not isinstance(row, tuple):
            iterators.append(row)
        else:
            iterable, shift_factor = row
            iterators.append(shift(iterable, shift_factor))
    return zip(*iterators)


def skip_first(iterator: IteratorOrIterable, n: int) -> tp.Iterator[T]:
    """
    Skip first n elements from given iterator
    """
    iterator = iter(iterator)
    for i in range(n):
        next(iterator)
    yield from iterator


def stop_after(iterator: IteratorOrIterable[T], n: int) -> tp.Iterator[T]:
    """
    Stop this iterator after returning n elements, even if it's longer than that.

    :param iterator: iterator or iterable to examine
    :param n: elements to return
    """
    iterator = iter(iterator)
    for i in range(n):
        yield next(iterator)


def n_th(iterator: IteratorOrIterable, n: int = 0) -> T:
    """
    Obtain n-th element (counting from 0) of an iterable

    :param n: element to return. Note that we're counting from 0
    :raises IndexError: iterable was too short
    """
    obj = iter(iterator)
    try:
        for i in range(n):
            next(obj)
        return next(obj)
    except (StopIteration, GeneratorExit):
        raise IndexError('Iterable was too short')


def take_n(iterator: IteratorOrIterable, n: int, skip: int = 0) -> tp.List[T]:
    """
    Take (first) n elements of an iterator, or the entire iterator, whichever comes first

    :param iterator: iterator to take from
    :param n: amount of elements to take
    :param skip: elements from the start to skip
    :return: list of p_len n (or shorter)
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
