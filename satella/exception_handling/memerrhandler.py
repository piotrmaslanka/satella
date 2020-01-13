import sys
import time
import typing as tp

from satella.posix import suicide
from .exception_handlers import BaseExceptionHandler, ALWAYS_FIRST, ExceptionHandlerCallable


class MemoryErrorExceptionHandler(BaseExceptionHandler):
    """
    A handler that terminates the entire process (or process group) is a MemoryError is seen.

    `custom_hook` is an exception callable to implement you own behavior. If it returns True,
    then MemoryErrorExceptionHandler won't kill anyone.
    """

    def __init__(self,
                 custom_hook: ExceptionHandlerCallable = lambda type_, value, traceback: False,
                 kill_pg: bool = False):
        """
        :param kill_pg: whether to kill entire process group, if applicable
        """
        super(MemoryErrorExceptionHandler, self).__init__()
        self.priority = ALWAYS_FIRST  # always run first!
        # so that we have some spare space in case a MemoryError is thrown
        self._free_on_memory_error = {'a': bytearray(1024 * 2)}
        self.custom_hook = custom_hook
        self.kill_pg = kill_pg
        self.installed = False

    def install(self):
        if self.installed:
            raise RuntimeError('already installed')

        from .global_eh import GlobalExcepthook
        GlobalExcepthook().add_hook(self)

    def handle_exception(self, type_, value, traceback) -> tp.Optional[bool]:
        if not issubclass(type_, MemoryError):
            return

        del self._free_on_memory_error['a']

        # noinspection PyBroadException
        try:
            if self.custom_hook(type_, value, traceback):
                return True
        except Exception as e:
            pass

        try:
            sys.stderr.write(
                'satella.exception_handling: MemoryError seen, killing\n')
            sys.stderr.flush()
        except (IOError, OSError):
            pass

        suicide(self.kill_pg)

        time.sleep(5)
        return True
