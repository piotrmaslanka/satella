import typing as tp
from abc import ABCMeta, abstractmethod



class RunActionAfterGeneratorCompletes(tp.Generator, metaclass=ABCMeta):
    """
    Run an action after a generator completes.
    An abstract class.

    Please note that this routine will be called only when the generator completes. If you abort it prematurely,
    via close()
    """

    __slots__ = 'generator', 'args', 'kwargs', 'closed', 'call_despite_closed'

    def __init__(self, generator: tp.Generator, *args, call_despite_closed: bool = False,
                 **kwargs):
        """
        :param generator: generator to watch for
        :param args: arguments to invoke action_to_run with
        :param call_despite_closed: :meth:`action_to_run` will be called even if the generator is closed
        :param call_on_exception: callable/1 with exception instance if generator somehow fails
        :param kwargs: keyword arguments to invoke action_to_run with
        """
        self.closed = False
        self.generator = generator
        self.args = args
        self.call_despite_closed = call_despite_closed
        self.kwargs = kwargs

    def close(self):
        """
        Close this generator. Note that this will cause :meth:`action_to_run` not to run
        """
        self.closed = True
        self.generator.close()

    def send(self, value):
        """Send a value to the generator"""
        try:
            return self.generator.send(value)
        except StopIteration:
            self._try_action_run()
            raise
        except Exception as e:
            self.call_on_exception(e)

    def next(self):
        return self.generator.__next__()

    def __iter__(self):
        return self

    def throw(self, __typ, __val=None, __tb=None):
        return self.generator.throw(__typ, __val, __tb)

    def __next__(self):
        try:
            return self.generator.__next__()
        except StopIteration:
            self._try_action_run()
            raise
        except Exception as e:
            self.call_on_exception(e)

    def _try_action_run(self):
        if not self.closed and not self.call_despite_closed:
            self.action_to_run(*self.args, **self.kwargs)

    @abstractmethod
    def action_to_run(self, *args, **kwargs):
        """This will run when this generator completes. Override it."""

    def call_on_exception(self, exc: Exception):
        """This will run when this generator throws any exception. Override it."""


def run_when_generator_completes(gen: tp.Generator, call_on_done: tp.Callable,
                                 *args, **kwargs) -> RunActionAfterGeneratorCompletes:
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
