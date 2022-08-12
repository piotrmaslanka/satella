import inspect
import threading

from .scope import Scope, logger

local_data = threading.local()
ENVIRONMENT_ENABLED = False


def tracing(event, *args):
    """
    Register for calls
    """
    if event != 'call' and event != 'return' and event != 'exception':
        return tracing

    if event == 'call':
        if not hasattr(local_data, 'satella_scope'):
            scope = Scope()
            inspect.currentframe().satella_scope = scope
            local_data.satella_scope = scope
        else:
            scope = Scope(local_data.satella_scope)
            local_data.satella_scope = scope
            inspect.currentframe().satella_scope = scope
    elif event == 'return':
        if local_data.current_scope.parent_scope is None:
            del local_data.satella_scope
        else:
            local_data.satella_scope = local_data.satella_scope.parent_scope
            local_data.satella_scope.send_to_parent()
    elif event == 'exception':
        scope = local_data.satella_scope
        scope.reset_data()
    return tracing


def enable_environment():
    """
    Enable Environment and it's features.

    .. warning:: This will register a trace function, and will slow down Python considerablyy.
        Sorry if this has nothing to do with shaving machines :(
    """
    global ENVIRONMENT_ENABLED
    if not ENVIRONMENT_ENABLED:
        from .scope import Scope
        ENVIRONMENT_ENABLED = True
        threading.settrace(tracing)
    else:
        ENVIRONMENT_ENABLED = True
