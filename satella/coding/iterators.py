import typing as tp

from satella.coding.recast_exceptions import silence_excs
from satella.coding.typing import NoArgCallable


def chain(*args) -> tp.Iterator:
    """
    Construct an iterator out of provided elements.

    If an element is an iterator, or an iterable it will be yielded-from. If it's not, it will
    just be yielded.

    A cast to iter() is used to determine iteratorness
    """
    for elem in args:
        try:
            yield from iter(elem)
        except TypeError:
            yield elem


def exhaust(iterator: tp.Iterator) -> None:
    """
    Iterate till the end of the iterator, discarding values as they go

    :param iterator: iterator to exhaust
    """
    try:
        while True:
            next(iterator)
    except StopIteration:
        pass


class SelfClosingGenerator:
    """
    A wrapper to exhaust the generator in response to closing it.

    This will allow generators to complete that don't provide a .close() method.

    This will additionally exhaust the generator upon deallocation of the generator.

    You can feed it with either generators, or generator-functions, it will behave correctly each
    time.

    You can also use it as a context manager, to decouple finalizing the generator from the GC
    collection
    """
    __slots__ = ('generator', 'stopped')

    def __init__(self, generator: tp.Union[tp.Generator, tp.Callable[[tp.Any], tp.Generator]]):
        self.generator = generator
        self.stopped = False  # type: bool

    def __iter__(self) -> 'SelfClosingGenerator':
        return self

    def __call__(self, *args, **kwargs):
        return SelfClosingGenerator(self.generator(*args, **kwargs))

    def send(self, obj: tp.Any) -> None:
        self.generator.send(obj)

    def __next__(self):
        try:
            return next(self.generator)
        except StopIteration:
            self.stopped = True
            raise

    def __enter__(self) -> 'SelfClosingGenerator':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.close()
        return False

    def close(self) -> None:
        if not self.stopped:
            # we might get a generator-generating function as an argument
            with silence_excs(TypeError):
                exhaust(self.generator)

            self.stopped = True

    def __del__(self):
        self.close()


# noinspection PyPep8Naming
class hint_with_length:
    """
    Accepting a generator, return it additionally providing
    a specified __length_hint__

    You can provide generator-generating functions as well

    :param generator: generator to decorate
    :param length: length hint to provide
    :param length_factory: a callable called with no arguments to get the length

    You must provide either length or length_factory. Giving them both is wrong, and
    will result in ValueError
    """
    __slots__ = ('generator', 'length', 'length_factory')

    def __init__(self, generator: tp.Generator, length: tp.Optional[int],
                 length_factory: tp.Optional[NoArgCallable[int]] = None):
        self.generator = generator
        if length is None and length_factory is None:
            raise ValueError('Give either length or length_factory')
        elif length is not None and length_factory is not None:
            raise ValueError('Give either length or length_factory')

        self.length = length
        self.length_factory = length_factory

    def __call__(self, *args, **kwargs):
        return hint_with_length(self.generator(*args, **kwargs), self.length)

    def close(self):
        return self.generator.close()

    def send(self, obj):
        return self.generator.send(obj)

    def __iter__(self) -> tp.Generator:
        return self.generator

    def __next__(self):
        return next(self.generator)

    def __length_hint__(self) -> int:
        if self.length is None:
            return self.length_factory()
        else:
            return self.length
