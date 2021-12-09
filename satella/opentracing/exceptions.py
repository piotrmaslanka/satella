import sys
import types
import typing as tp

from satella.coding.typing import ExceptionClassType
from satella.instrumentation import Traceback
from satella.opentracing.trace import Span

max_traceback_length = 65536


def set_maximum_traceback_length(length: int) -> None:
    """
    Set a new maximum traceback length

    :param length: maximum traceback length, in bytes
    """
    global max_traceback_length
    max_traceback_length = length


def trace_exception(span: tp.Optional[Span], exc_type: tp.Optional[ExceptionClassType] = None,
                    exc_val: tp.Optional[Exception] = None,
                    exc_tb: tp.Optional[types.TracebackType] = None,
                    max_tb_length: tp.Optional[int] = None) -> None:
    """
    Log an exception's information to the chosen span, as logs and tags.

    :param span: span to log into or None for a no-op
    :param exc_type: exception type. If None this will be taken from sys.exc_info.
    :param exc_val: exception value. If None this will be taken from sys.exc_info.
    :param exc_tb: exception traceback. If None this will be taken from sys.exc_info.
    :param max_tb_length: maximum traceback length. If traceback is longer than that,
        it will be trimmed. The default is 65536. You can set it by
        :meth:`satella.opentracing.set_maximum_traceback_length`
    """
    if span is None:
        return

    max_tb_length = max_tb_length or max_traceback_length

    if exc_type is None:
        exc_type, exc_val, exc_tb = sys.exc_info()
        if exc_type is None:
            return

    tb = Traceback(exc_tb.tb_frame).pretty_format()
    if len(tb) > max_tb_length:
        tb = tb[:max_tb_length]

    span.set_tag('error', True)
    span.log_kv({'event': 'error',
                 'message': str(exc_val),
                 'error.object': exc_val,
                 'error.kind': exc_type,
                 'stack': tb
                 })
