from __future__ import print_function, absolute_import, division

import logging
import os
import typing as tb
import typing.io as iotb
import uuid

from satella.coding import silence_excs
from satella.instrumentation import Traceback
from .exception_handlers import BaseExceptionHandler

logger = logging.getLogger(__name__)

__all__ = [
    'DumpToFileHandler'
]

AsStreamTypeAccept = tb.Union[str, tb.IO, None]
AsStreamTypeAcceptHR = tb.Union[str, tb.TextIO]
AsStreamTypeAcceptBIN = tb.Union[str, tb.BinaryIO]


class AsStream:
    MODE_FILE = 0
    MODE_STREAM = 1
    MODE_DEVNULL = 2

    def __init__(self, o: AsStreamTypeAccept, human_readable):
        self.o = o
        self.human_readable = human_readable

        if isinstance(o, str):
            if os.path.isdir(o):
                o = os.path.join(o, uuid.uuid4().hex)

            self.mode = AsStream.MODE_FILE

        elif hasattr(o, 'write'):
            self.mode = AsStream.MODE_STREAM

        elif o is None:
            self.mode = AsStream.MODE_DEVNULL
        else:
            raise TypeError('invalid stream object')

    def __enter__(self) -> tb.Union[iotb.TextIO, iotb.BinaryIO]:
        if self.mode == AsStream.MODE_FILE:
            self.file = open(self.o, 'w' if self.human_readable else 'wb',
                             encoding='utf8' if self.human_readable else None)
            return self.file.__enter__()
        elif self.mode == AsStream.MODE_STREAM:
            return self.o
        elif self.mode == AsStream.MODE_DEVNULL:
            class NoopFile(object):
                def write(self, v):
                    pass

                def flush(self):
                    pass

            self.o = NoopFile()
            return self.o

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.mode == AsStream.MODE_FILE:
            return self.file.__exit__(exc_type, exc_val, exc_tb)
        elif self.mode == AsStream.MODE_STREAM:
            with silence_excs(AttributeError):
                self.o.flush()
        elif self.mode == AsStream.MODE_DEVNULL:
            pass


class DumpToFileHandler(BaseExceptionHandler):
    """
    Write the stack trace to a stream-file
    """

    def __init__(self, human_readables: tb.Iterable[AsStreamTypeAcceptHR],
                 trace_pickles: tb.Iterable[AsStreamTypeAcceptBIN]=[]):
        """
        :param human_readables: iterable of either a file-like objects, or paths where human-readable files will be output
        :param trace_pickles: iterable of either a file-like objects, or paths where pickles with stack status will be output
        """
        super(DumpToFileHandler, self).__init__()
        self.hr = [AsStream(x, True) for x in human_readables]
        self.tp = [AsStream(x, False) for x in trace_pickles]

    def handle_exception(self, type_, value, traceback):
        try:
            tb = Traceback()
        except ValueError:
            return  # no traceback, probably hit KeyboardInterrupt or SystemExit

        for q in self.hr:
            with q as f:
                f.write('Unhandled exception caught: \n')
                tb.pretty_print(output=f)

        for q in self.tp:
            with q as f:
                f.write(tb.pickle())
