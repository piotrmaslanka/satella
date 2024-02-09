Variable managers
=================

.. note:: Previously these were called context managers. To avoid mistakes
    they were renamed to variable managers.

Variable managers are convenient way to store sets of variables as contexts,
ie. global configuration. They replace global settings in way that's easily
testable, easy to reason about and reasonably quick.
Thy're quite similar to Werkzeug's contextlocals_.


.. _contextlocals: https://werkzeug.palletsprojects.com/en/2.1.x/local/

Let's provide an example. You have a `settings.py` file:

.. code-block:: python

    ATOMIC_REQUESTS = True
    DATABASE_DIRECTORY = '/var/opt/satella/database-directory'

And somewhere is a code that uses these

Context manager are convenient ways to

.. autoclass:: satella.coding.var_managers.Context
    :members:


.. autoclass:: satella.coding.var_managers.ThreadContext
    :members:


.. autofunction:: satella.coding.var_managers.get_current_context
