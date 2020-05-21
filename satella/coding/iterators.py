import typing as tp


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


