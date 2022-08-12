Debug
=====

Satella contains useful routines to help you with debugging your apps.

Debugging will look like inserting some statements into your code
from satella, and then, when your bug is fixed, you just remove them.

Environment
-----------

A Scope is created for each function call. In a nutshell, Scope
is a way to attach more functionality to thread-local scopes.
Each time a new function is called a new :py:class:`satella.debug.environment.Scope`
is defined, allowing access to it's parent data. Upon a Scope expiring (this stack frame being deinitialized)
it updates the parent with it's contents.

Note however that data for Scope which has finished with an Exception will be discarded.

.. autofunction:: satella.debug.tracing.enable_environment

.. autoclass:: satella.debug.tracing.Scope
    :members:
