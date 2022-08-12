import inspect
import threading

from .scope import Scope

local_data = threading.local()
ENVIRONMENT_ENABLED = False


def tracing(event, arg):
    if event != 'call' and event != 'return' and event != 'exception':
        return tracing

    if event == 'call':
        if not hasattr(local_data, 'current_scope'):
            scope = Scope()
            inspect.currentframe().satella_scope = scope
            local_data.current_scope = scope
        else:
            scope = Scope(local_data.current_scope)
            local_data.current_scope = scope
            inspect.currentframe().satella_scope = scope
    elif event == 'return':
        if hasattr(local_data, 'current_scope'):
            scope: Scope = local_data.current_scope
            if scope.parent_scope is None:
                del local_data.current_scope
            else:
                local_data.current_scope = scope.parent_scope
                scope.send_to_parent()
    elif event == 'exception':
        from .scope import EXCLUDED_VALUES
        scope = local_data.current_scope
        scope.__dict__ = {k: v for k, v in scope.__dict__.items() if k not in EXCLUDED_VALUES}
    return tracing


def enable_environment():
    """
    Enable Environment and it's features.

    .. warning:: This will register a trace function, and will slow down Python considerably
    """
    global ENVIRONMENT_ENABLED
    ENVIRONMENT_ENABLED = True
    threading.settrace(tracing)
