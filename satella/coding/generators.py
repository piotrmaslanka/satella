import typing as tp
from abc import ABCMeta, abstractmethod


class RunActionAfterGeneratorCompletes(metaclass=ABCMeta):
    """
    Run an action after a generator completes.
    An abstract class.
    """

    __slots__ = 'generator', 'args', 'kwargs'

    def __init__(self, generator: tp.Generator, *args, **kwargs):
        """
        :param generator: generator to watch for
        :param args: arguments to invoke action_to_run with
        :param kwargs: keyword arguments to invoke action_to_run with
        """
        self.generator = generator
        self.args = args
        self.kwargs = kwargs

    def send(self, value):
        """Send a value to the generator"""
        self.generator.send(value)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self.generator)
        except StopIteration:
            self.action_to_run(*self.args, **self.kwargs)
            raise

    @abstractmethod
    def action_to_run(self):
        """This will run when this generator completes. Override it."""


def run_when_generator_completes(gen: tp.Generator, call_on_done: tp.Callable[[], None],
                                 *args, **kwargs) -> tp.Generator:
    """
    Return the generator with call_on_done to be called on when it finishes

    :param gen: generator
    :param call_on_done: callable/0 to call on generator's completion
    :param args: args to pass to the callable
    :param kwargs: kwargs to pass to the callable
    :returns: generator
    """
    class Inner(RunActionAfterGeneratorCompletes):
        def action_to_run(self, *args, **kwargs):
            call_on_done(*args, **kwargs)

    return Inner(gen, *args, **kwargs)
