import sys
import time
import typing as tp

from satella.coding.recast_exceptions import silence_excs
from ..os.misc import suicide
from .exception_handlers import BaseExceptionHandler, ALWAYS_FIRST, ExceptionHandlerCallable


class MemoryErrorExceptionHandler(BaseExceptionHandler):
    """
    A handler that terminates the entire process (or process group) is a MemoryError is seen.

    `custom_hook` is an exception callable to implement you own behavior. If it returns True,
    then MemoryErrorExceptionHandler won't kill anyone. You can also provide a CallableGroup
    with gather=True - if any of callables returns True, the process won't be killed.

    :param kill_pg: whether to kill entire process group, if applicable
    """
    __slots__ = ('priority', '_free_on_memory_error', 'custom_hook', 'kill_pg', 'installed')

    def __init__(self,
                 custom_hook: ExceptionHandlerCallable = lambda type_, value, traceback: False,
                 kill_pg: bool = False):
        super().__init__(ALWAYS_FIRST)
        # so that we have some spare space in case a MemoryError is thrown
        self._free_on_memory_error = {'a': bytearray(1024 * 2)} # type: tp.Dict[str, bytearray]
        self.custom_hook = custom_hook                  # type: ExceptionHandlerCallable
        self.kill_pg = kill_pg                          # type: bool
        self.installed = False                          # type: bool

    def install(self):
        if self.installed:
            raise RuntimeError('already installed')

        from .global_eh import GlobalExcepthook
        GlobalExcepthook().add_hook(self)

    def handle_exception(self, type_, value, traceback) -> tp.Optional[bool]:
        if not issubclass(type_, MemoryError):
            return

        with silence_excs(KeyError):
            del self._free_on_memory_error['a']

        # noinspection PyBroadException
        with silence_excs(Exception):
            val = self.custom_hook(type_, value, traceback)
            if isinstance(val, tp.Sequence):
                val = any(val)

            if val:
                return True

        try:
            sys.stderr.write(
                'satella.exception_handling: MemoryError seen, killing\n')
            sys.stderr.flush()
        except (IOError, OSError):
            pass

        suicide(self.kill_pg)

        time.sleep(5)
        return True
