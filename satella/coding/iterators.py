import typing as tp


def exhaust(iterator: tp.Iterator):
    """
    Iterate till the end of the iterator, discarding values as they go

    :param iterator: iterator to exhaust
    """
    try:
        while True:
            next(iterator)
    except (GeneratorExit, StopIteration):
        pass


class SelfClosingGenerator:
    """
    A wrapper to exhaust the generator in response to closing it.

    This will allow generators to complete that don't provide a .close() method.

    This will additionally exhaust the generator upon deallocation of the generator.

    You can feed it with either generators, or generator-functions, it will behave correctly each time.
    """
    __slots__ = ('generator', 'stopped')

    def __init__(self, generator: tp.Generator):
        self.generator = generator
        self.stopped = False

    def __iter__(self):
        return self.generator

    def __call__(self, *args, **kwargs):
        return SelfClosingGenerator(self.generator(*args, **kwargs))

    def send(self, obj: tp.Any):
        self.generator.send(obj)

    def __next__(self):
        try:
            return next(self.generator)
        except (StopIteration, GeneratorExit):
            self.stopped = True
            raise

    def close(self):
        if not self.stopped:
            try:
                exhaust(self.generator)
            except TypeError:
                pass
            self.stopped = True
        raise GeneratorExit()

    def __del__(self):
        try:
            self.close()
        except GeneratorExit:
            pass


# noinspection PyPep8Naming
class hint_with_length:
    """
    Accepting a generator, return it additionally providing
    a specified __length_hint__

    :param generator: generator to decorate
    :param length: length hint to provide
    """

    __slots__ = ('generator', 'length')

    def __init__(self, generator: tp.Generator, length: int):
        self.generator = generator
        self.length = length

    def __iter__(self):
        return self.generator

    def __next__(self):
        return next(self.generator)

    def __length_hint__(self) -> int:
        return self.length


