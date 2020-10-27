import sys
import types
import typing as tp

from satella.coding.typing import ExceptionClassType
from satella.instrumentation import Traceback
from satella.opentracing.trace import Span


def trace_exception(span: Span, exc_type: tp.Optional[ExceptionClassType] = None,
                    exc_val: tp.Optional[Exception] = None,
                    exc_tb: tp.Optional[types.TracebackType] = None) -> None:
    """
    Log an exception's information to the chosen span, as logs and tags.

    :param span: span to log into
    :param exc_type: exception type. If None this will be taken from sys.exc_info.
    :param exc_val: exception value. If None this will be taken from sys.exc_info.
    :param exc_tb: exception traceback. If None this will be taken from sys.exc_info.
    """
    if exc_type is None:
        exc_type, exc_val, exc_tb = sys.exc_info()
        if exc_type is None:
            return

    span.set_tag('error', True)
    span.log_kv({'event': 'error',
                 'message': str(exc_val),
                 'error.object': exc_val,
                 'error.kind': exc_type,
                 'stack': Traceback(exc_tb.tb_frame).pretty_format()
                 })
