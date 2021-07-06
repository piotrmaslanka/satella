=========
Traceback
=========

Traceback object is used to preserve all the information you can get
in case of an exception. It preserves:
* Information about all stack frames in this thread
* Every local and global variable at every stack frame
    * If the variable is picklable, and pickling is enabled, it is pickled on the spot
    * Variable's _repr_ is always preserved
    * Of course variable name is saved

It also allows to pretty print the exception. Traceback is picklable, so you
can safely do so and analyze the exception at your own leisure.

Unpickling _Traceback_ objects in any environment is safe. However, obtaining
variable values via _load_value_ might be not.

Usage:

::

    from satella.instrumentation import Traceback

    try:
        ...
    except:
        tb = Traceback()

        print(tb.pretty_print())    # print stack trace

        tb_p = tb.pickle()  # pickles the traceback

Traceback should be created in the exception it is supposed to capture,
as it captures exception info from _sys.exc_info()_.
If no exception is in progress, current stack frame will be fetched
from `inspect.currentframe()`.

Alternatively, you can pass a `<frame>` object to Traceback, in order to serialize it, for example:

::

    import sys

    frame_1 = next(iter(sys._current_frames().values()))
    tb = Traceback(frame_1)

.. autoclass:: satella.instrumentation.Traceback
    :members:

.. autoclass:: satella.instrumentation.StoredVariableValue
    :members:

.. autoclass:: satella.instrumentation.StackFrame
    :members:

.. autoclass:: satella.instrumentation.GenerationPolicy
    :members:

There's a helper function as well

.. autofunction:: satella.instrumentation.frame_from_traceback

Dumping all stack frames
------------------------

.. autofunction:: satella.instrumentation.dump_frames_on

.. autofunction:: satella.instrumentation.install_dump_frames_on
