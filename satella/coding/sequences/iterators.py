import collections
import itertools
import typing as tp
import warnings

from ..decorators import for_argument, wraps
from ..recast_exceptions import rethrow_as, silence_excs
from ..typing import Iteratable, T, U, Predicate, V, K


def iterate_callable(clbl: tp.Callable[[int], V], start_from: int = 0,
                     exc_classes=(IndexError, ValueError)) -> tp.Iterator[V]:
    """
    Given a callable that accepts an integer and returns the n-th entry, iterate over
    it until it starts to throw some exception.

    :param clbl: callable to call
    :param start_from: number to start from
    :param exc_classes: exceptions that being thrown show that the list was exhausted

    :return: an iterator
    """
    for i in itertools.count(start_from):
        try:
            yield clbl(i)
        except exc_classes:
            return


def try_close(iterator: tp.Iterator) -> None:
    """
    Try to invoke close() on an iterator. Do nothing if provided iterator doesn't have a .close()
    method.

    :param iterator: iterator to close
    """
    try:
        iterator.close()
    except AttributeError:
        pass


def length(iterator: Iteratable) -> int:
    """
    Return the length of an iterator, exhausting it by the way
    """
    i = 0
    for _ in iterator:
        i += 1
    return i


def f_range(*args: float) -> tp.Iterator[float]:
    """
    A range() that supports float.

    Note that this behaves correctly when given a negative step.

    Call either:

    >>> f_range(stop)   # will start from 0 and step 1
    >>> f_range(start, stop)    # will start from start and continue until the result is gte stop
    >>> # will start from start and continue by step until the result is gte stop
    >>> f_range(start, stop, step)

    :raise TypeError: invalid number of arguments
    """
    len_args = len(args)
    if len_args == 1:
        start, step = 0, 1
        stop = args[0]
    elif len_args == 2:
        start, stop = args
        step = 1
    elif len_args == 3:
        start, stop, step = args
    else:
        raise TypeError('Invalid number of arguments')

    def iterate(f_start, f_stop, f_step):
        if f_step > 0:
            while f_start < f_stop:
                yield f_start
                f_start += f_step
        else:
            while f_start > f_stop:
                yield f_start
                f_start += f_step

    return iterate(start, stop, step)


def append_sequence(seq: tp.Iterator[tuple], *elems_to_append) -> tp.Iterator[tuple]:
    """
    Return an iterator which append elem_to_append to every tuple in seq.

    Example:

    >>> a = [(1, ), (2, ), (3, )]
    >>> assert list(append_sequence(a, 1, 2)) == [(1, 1, 2), (2, 1, 2), (3, 1, 2)]

    If every element of seq is not a tuple, it will be cast to one.

    :param seq: sequence to append
    :param elems_to_append: element(s) to append
    :return: an iterator
    """
    for tpl in seq:
        if not isinstance(tpl, tuple):
            tpl = tuple(tpl)
        yield tpl + elems_to_append


def walk(obj: T, child_getter: tp.Callable[[T], tp.Optional[tp.List[T]]] = list,
         deep_first: bool = True,
         leaves_only: bool = False) -> tp.Iterator[T]:
    """
    Return every node of a nested structure.

    :param obj: structure to traverse. This will not appear in generator
    :param child_getter: a callable to return a list of children of T.
        Should return an empty list or None of there are no more children.
    :param deep_first: if True, deep first will be returned, else it will be breadth first
    :param leaves_only: if True, only leaf nodes (having no children) will be returned
    """
    a = ConstruableIterator(child_getter(obj))
    for o in a:
        children = child_getter(o)
        if children is not None:
            try:
                child_len = len(children)
            except TypeError:
                child_len = 0

            if child_len:
                if deep_first:
                    a.add_many_immediate(children)
                else:
                    a.add_many(children)
                if leaves_only:
                    continue

        yield o


class ConstruableIterator:
    """
    An iterator that you can attach arbitrary things at the end and consume them during iteration.
    Eg:

    >>> a = ConstruableIterator([1, 2, 3])
    >>> for b in a:
    >>>   if b % 2 == 0:
    >>>       a.add(6)

    All arguments you provide to the constructor will be passed to underlying deque
    """
    __slots__ = ('entries',)

    def __init__(self, *args, **kwargs):
        self.entries = collections.deque(*args, **kwargs)

    def add_immediate(self, t: T) -> None:
        """
        Schedule given value to be iterated over during the next __next__ call

        :param t: value to iterate over
        """
        self.entries.appendleft(t)

    def add_many_immediate(self, t: tp.Iterable[T]) -> None:
        """
        Schedule given values to be iterated over during the next __next__ call

        :param t: values to iterate over
        """
        for i, entry in enumerate(t):
            self.entries.insert(i, entry)

    def add(self, t: T) -> None:
        """
        Schedule given value to be iterated over after current items

        :param t: value to iterate over
        """
        self.entries.append(t)

    def add_many(self, t: tp.Iterable[T]) -> None:
        """
        Schedule given values to be iterated over after current items

        :param t: iterable of values
        """
        self.entries.extend(t)

    def __iter__(self) -> 'ConstruableIterator':
        return self

    @rethrow_as(IndexError, StopIteration)
    def __next__(self) -> T:
        return self.entries.popleft()

    def __length_hint__(self) -> int:
        return len(self.entries)


class AlreadySeen(tp.Generic[K]):
    """
    Class to filter out unique objects. Objects must be hashable, barring that
    they must be eq-able, however passing it an non-hashable object will result in
    O(n^2) complexity, as the class uses a list to keep track of the objects.

    Usage:

    >>> als = AlreadySeen()
    >>> for elem in sequence:
    >>>     if als.is_unique(elem):
    >>>         ... process the element ...
    """
    __slots__ = ('set',)

    def __init__(self):
        self.set = None     # type: tp.Union[list, set]

    def is_unique(self, key: K) -> bool:
        """
        Has the element been spotted first time?

        Add it to the set.

        :param key: element to check
        :return: whether the element was seen for the first time
        """
        try:
            hash(key)
            if self.set is None:
                self.set = set()
            if key in self.set:
                return False
            self.set.add(key)
            return True
        except TypeError:
            warnings.warn('Passed argument is not hashable, you pay with '
                          'O(n^2) complexity!', RuntimeWarning)
            if self.set is None:
                self.set = []
            if key in self.set:
                return False
            self.set.append(key)
            return True


def unique(lst: Iteratable) -> tp.Iterator[T]:
    """
    Return each element from lst, but return every element only once.

    Take care for elements of T to be __eq__-able and hashable!

    This will keep internally a set of elements encountered, and skip them if same element
    appears twice

    :param lst: iterable to process
    :return: a generator yielding unique items from lst
    """
    already_seen = set()
    for elem in lst:
        if elem not in already_seen:
            already_seen.add(elem)
            yield elem


@for_argument(iter)
def even(sq: Iteratable) -> tp.Iterator[T]:
    """
    Return only elements with even indices in this iterable (first element will be returned,
    as indices are counted from 0)
    """
    while True:
        try:
            yield next(sq)
            next(sq)
        except StopIteration:
            return


@silence_excs(StopIteration)
@for_argument(iter)
def odd(sq: Iteratable) -> tp.Iterator[T]:
    """
    Return only elements with odd indices in this iterable.
    """
    while True:
        try:
            next(sq)
            yield next(sq)
        except StopIteration:
            return


def count(sq: Iteratable, start: tp.Optional[int] = None, step: int = 1,
          start_at: tp.Optional[int] = None) -> tp.Iterator[int]:
    """
    Return a sequence of integers, for each entry in the sequence with provided step.

    Essentially the same (if step were ignored) as:

    >>> (i for i, x in enumerate(sq, start=start_at))

    .. deprecated:: 2.14.22
        Use `start` instead

    :param sq: sequence to enumerate
    :param start: alias for start_at. Prefer it in regards to start_at. Default is 0
    :param step: number to add to internal counter after each element
    :param start_at: deprecated alias for start
    :return: an iterator of subsequent integers
    """
    if start_at:
        warnings.warn('This is deprecated and will be removed in Satella 3.0. Use start instead.',
                      DeprecationWarning)
        start = start_at
    num = start or 0
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


def infinite_counter(start_at: int = 0, step: int = 1) -> tp.Iterator[int]:
    """
    Infinite counter, starting at start_at

    .. deprecated:: 2.14.22
        Use `itertools.count` instead.

    :param start_at: value at which to start counting. It will be yielded as first
    :param step: step by which to progress the counter
    """
    warnings.warn('This is deprecated and will be removed in Satella 3.0, '
                  'use itertools.count() instead', DeprecationWarning)
    i = start_at
    while True:
        yield i
        i += step


def is_instance(classes: tp.Union[tp.Tuple[type, ...], type]) -> Predicate[object]:
    def inner(object_):
        return isinstance(object_, classes)

    inner.__doc__ = """Return a bool telling if object is of type %s""" % (repr(classes),)
    return inner


@for_argument(iter, iter)
def other_sequence_no_longer_than(base_sequence: Iteratable,
                                  other_sequence: Iteratable) -> tp.Iterator[T]:
    """
    Return every item in other_sequence, but limit it's p_len to that of base_sequence.

    If other_sequence is shorter than base_sequence, the shorter one will be returned.

    :param base_sequence: sequence whose p_len should be taken
    :param other_sequence: sequence to output values from
    """
    while True:
        try:
            next(base_sequence)
            yield next(other_sequence)
        except StopIteration:
            return


def shift(iterable_: tp.Union[tp.Reversible[T], Iteratable],
          shift_factor: int) -> tp.Iterator[T]:
    """
    Return this sequence, but shifted by factor elements, so that elements will appear
    sooner by factor.

    Eg:

    >>> assert list(shift([1,2, 3], 1)) == [2, 3, 1]

    However note that this will result in iterators which have negative shift to be readed entirely
    into memory (converted internally to lists). This can be avoided by passing in a Reversible
    iterable.

    :param iterable_: iterable to shift
    :param shift_factor: factor by which shift elements.
    :return: shifted sequence
    """

    if shift_factor >= 0:
        iterator = iter(iterable_)
        elements = []
        for i in range(shift_factor):
            elements.append(next(iterator))
        return itertools.chain(iterator, elements)
    else:
        if hasattr(iterable_, '__reversed__'):
            elements = take_n(reversed(iterable_), -shift_factor)
            elements = reversed(elements)
            return other_sequence_no_longer_than(iterable_, itertools.chain(elements, iterable_))
        else:
            iterator = list(iterable_)
            iterator = iterator[shift_factor:] + iterator[:shift_factor]  # shift's already negative
            return iterator


@silence_excs(StopIteration)
def zip_shifted(*args: tp.Union[Iteratable, tp.Tuple[Iteratable, int]]) -> \
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

    .. deprecated:: 2.14.22
        Use `zip(shift(...))` instead

    :param args: a tuple with the iterator/iterable and amount of shift. If a non-tuple is given,
        it is assumed that the shift is zero.
    """
    warnings.warn('This is deprecated and will be removed in Satella 3.0. '
                  'Use zip(shift(...)) instead!', DeprecationWarning)

    iterators = []  # type: tp.List[tp.Union[tp.Tuple[tp.Iterator[T], tp.List[T]], tp.Iterator[T]]
    for row in args:
        if not isinstance(row, tuple):
            iterators.append(row)
        else:
            iterable, shift_factor = row
            iterators.append(shift(iterable, shift_factor))
    return zip(*iterators)


@for_argument(iter)
@silence_excs(StopIteration)
def skip_first(iterator: Iteratable, n: int) -> tp.Iterator[T]:
    """
    Skip first n elements from given iterator.

    Returned iterator may be empty, if source iterator is shorter or equal to n.

    .. deprecated:: 2.14.22
        Use `itertools.islice` instead
    """
    warnings.warn('This is deprecated and will be removed in Satella 3.0. '
                  'Please use itertools.islice instead', DeprecationWarning)

    for i in range(n):
        next(iterator)
    yield from iterator


class _ListWrapperIteratorIterator(tp.Iterator[T]):
    __slots__ = ('parent', 'pos')

    def __init__(self, parent):
        self.parent = parent
        self.pos = 0

    def __length_hint__(self) -> int:
        return len(self.parent.list)

    def __iter__(self) -> tp.Iterator[T]:
        return self

    def __next__(self) -> T:
        if self.pos >= len(self.parent.list):
            item = self.parent.next()
        else:
            item = self.parent.list[self.pos]
        self.pos += 1
        return item


class ListWrapperIterator(tp.Generic[T]):
    """
    A wrapped for an iterator, enabling using it as a normal list.

    The first time this is evaluated, list is populated with elements.

    The second time, items are taken from the list.

    It never computes more than it needs to.

    Essentially a class that lets you reuse one-shot iterators.
    """
    __slots__ = ('iterator', 'exhausted', 'list')

    def __init__(self, iterator: Iteratable):
        self.iterator = iter(iterator)
        self.exhausted = False
        self.list = []

    def exhaust(self) -> None:
        """
        Load all elements of this iterator into memory.
        """
        if self.exhausted:
            return
        for elem in self.iterator:
            self.list.append(elem)
        self.exhausted = True

    def advance_to_item(self, i: int) -> None:
        """
        Makes the list be at least i in size
        """
        if self.exhausted:
            return

        while len(self.list) < i:
            try:
                self.list.append(next(self.iterator))
            except StopIteration:
                self.exhausted = True
                return

    def __len__(self) -> int:
        self.exhaust()
        return len(self.list)

    def __getitem__(self, item: tp.Union[slice, int]) -> tp.Union[tp.List[T], T]:
        if isinstance(item, int):
            if len(self.list) < item + 1:
                self.advance_to_item(item + 1)
        else:
            self.advance_to_item(item.stop)
        return self.list[item]

    def next(self) -> T:
        """
        Get the next item

        :raises StopIteration: next element is not available due to iterator finishing
        """
        if self.exhausted:
            raise StopIteration()
        else:
            item = next(self.iterator)
            self.list.append(item)
            return item

    def __iter__(self) -> tp.Iterator[T]:
        return _ListWrapperIteratorIterator(self)


@silence_excs(StopIteration)
@for_argument(iter)
def stop_after(iterator: Iteratable, n: int) -> tp.Iterator[T]:
    """
    Stop this iterator after returning n elements, even if it's longer than that.

    The resulting iterator may be shorter than n, if the source element is so.

    .. deprecated:: 2.14.22
        Use `itertools.islice` instead

    :param iterator: iterator or iterable to examine
    :param n: elements to return
    """
    warnings.warn('This is deprecated and will be removed in Satella 3.0. '
                  'Please use itertools.islice instead', DeprecationWarning)

    for i in range(n):
        yield next(iterator)


@for_argument(iter)
def n_th(iterator: Iteratable, n: int = 0) -> T:
    """
    Obtain n-th element (counting from 0) of an iterable

    :param iterator: iterable to process
    :param n: element to return. Note that we're counting from 0
    :raises IndexError: iterable was too short
    """
    try:
        for i in range(n):
            next(iterator)
        return next(iterator)
    except (StopIteration, GeneratorExit):
        raise IndexError('Iterable was too short')


class IteratorListAdapter:
    """
    A wrapper around an iterator that enables it to be processed as a list.

    Ie. the generator will now support __contains__, __len__ and __getitem__.
    If a call to such a method is done, the generator will be unfolded in memory so this
    might take a ton of memory! You've been warned!

    :param iterator:
    """
    __slots__ = ('unfolded', 'iterator', 'list', 'pointer')

    def __init__(self, iterator: tp.Iterator):
        self.iterator = iter(iterator)
        self.list = None
        self.unfolded = False
        self.pointer = 0

    def __iter__(self):
        if self.unfolded:
            return iter(self.list)
        else:
            return self

    @rethrow_as(IndexError, StopIteration)
    def __next__(self):
        if self.unfolded:
            self.pointer += 1
            return self.list[self.pointer - 1]  # throws: IndexError
        else:
            return next(self.iterator)

    def __unfold(self):
        if self.unfolded:
            return
        self.list = list(self.iterator)
        self.unfolded = True
        self.pointer = 0

    def __getitem__(self, item):
        self.__unfold()
        return self.list[item]

    def __contains__(self, item) -> bool:
        self.__unfold()
        return item in self.list

    def __len__(self) -> int:
        self.__unfold()
        return len(self.list)


@silence_excs(StopIteration, returns=True)
def is_empty(iterable: Iteratable, exhaust: bool = True) -> bool:
    """
    Checks whether an iterator is empty.

    This will exhaust the iterator if exhaust is left at default, or True

    :param iterable: iterator to check
    :param exhaust: if set to False, at most a single element will be consumed
        from the iterator
    :return: whether the iterator is empty
    """
    iterator = iter(iterable)
    if exhaust:
        i = 0
        for _ in iterator:
            i += 1
        return i == 0
    else:
        next(iterator)
        return False


def map_list(fun: tp.Callable, iterable: Iteratable) -> tp.List:
    """
    A syntactic sugar for

    >>> list(map(fun, iterable))

    :param fun: function to apply
    :param iterable: iterable to iterate over
    """
    return list(map(fun, iterable))


def to_iterator(fun):
    """
    Convert function to an iterator. You can replace the following code:

    >>> def iterator(x):
    >>>     for y in x:
    >>>         yield fun(y)

    with

    >>> @to_iterator
    >>> def fun(y):
    >>>     ...

    and now call fun instead of iterator. fun will accept a single argument - the iterable,
    and assume that the function you decorate also takes a single argument - the item
    """

    @wraps(fun)
    def inner(iterable):
        for item in iterable:
            yield fun(item)

    return inner


def smart_zip(*iterators: Iteratable) -> tp.Iterator[tp.Tuple[T, ...]]:
    """
    Zip in such a way that resulted tuples are automatically expanded.

    Ie:

    >>> b = list(smart_zip([(1, 1), (1, 2)], [1, 2]))
    >>> assert b == [(1, 1, 1), (1, 2, 2)]

    Note that an element of the zipped iterator must be a tuple (ie. isinstance tuple)
    in order for it to be appended to resulting iterator element!

    :param iterators: list of iterators to zip together
    :return: an iterator zipping the arguments in a smart way
    """
    for row in zip(*iterators):
        a = []
        for elem in row:
            if isinstance(elem, tuple):
                a.extend(elem)
            else:
                a.append(elem)
        yield tuple(a)


def enumerate2(iterable: Iteratable, start: int = 0,
               step: int = 1) -> tp.Iterator[tp.Tuple[int, T]]:
    """
    Enumerate with a custom step

    :param iterable: iterable to enumerate
    :param start: value to start at
    :param step: step to add during each iteration
    """
    v = start
    for item in iterable:
        yield v, item
        v += step


def smart_enumerate(iterator: Iteratable, start: int = 0,
                    step: int = 1) -> tp.Iterator[tp.Tuple]:
    """
    An enumerate that talks pretty with lists of tuples. Consider

    >>> a = [(1, 2), (3, 4), (5, 6)]
    >>> for i, b in enumerate(a):
    >>>     c, d = b
    >>>     ...

    This function allows you just to write:
    >>> for i, c, d in enumerate(a):
    >>>     ...

    Note that elements in your iterable must be either a list of a tuple for that to work,
    or need to be able to be coerced to a tuple. Otherwise, TypeError will be thrown.

    :param iterator: iterator to enumerate
    :param start: value to start counting at
    :param step: step to advance the enumeration with
    :raise TypeError: could not coerce the elements in your iterable to a tuple
    """
    i = start
    for row in iterator:
        if isinstance(row, tuple):
            yield (i,) + row
        else:
            yield (i,) + tuple(row)
        i += step


@for_argument(iter)
def take_n(iterator: Iteratable, n: int, skip: int = 0) -> tp.List[T]:
    """
    Take (first) n elements of an iterator, or the entire iterator, whichever comes first

    :param iterator: iterator to take from
    :param n: amount of elements to take
    :param skip: elements from the start to skip
    :return: list of p_len n (or shorter)
    """
    for i in range(skip):
        next(iterator)

    output = []
    for i in range(n):
        try:
            output.append(next(iterator))
        except StopIteration:
            return output
    return output
