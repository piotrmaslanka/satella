Sources
=======

At the core of your config files, there are Sources. A Source is a single source of configuration - it could be
an environment variable, or a particular file, or a directory full of these files.

.. autoclass:: satella.configuration.sources.StaticSource
    :members:

.. autoclass:: satella.configuration.sources.StaticSource
    :members:

.. autoclass:: satella.configuration.sources.EnvironmentSource
    :members:

.. autoclass:: satella.configuration.sources.EnvVarsSource
    :members:

.. autoclass:: satella.configuration.sources.FileSource
    :members:

.. autoclass:: satella.configuration.sources.DirectorySource
    :members:


Then there are abstract sources of configuration.

.. autoclass:: satella.configuration.sources.AlternativeSource
    :members:

.. autoclass:: satella.configuration.sources.OptionalSource
    :members:

.. autoclass:: satella.configuration.sources.MergingSource
    :members:



JSON schema
-----------

The JSON schema consists of defining particular sources, embedded in one another.

::

    {
        "type": "ClassNameOfTheSource",
        "args": [
        ],
        "kwarg_1": ...,
        "kwarg_2": ...,
    }

If an argument consists of a dict with ``type`` key, it will be also loaded and passed internally as a source.
Two reserved types are ``lambda``, which expects to have a key of ``operation``. This will be appended to
``lambda x: `` and ``eval()``-uated.

Always you can provide a key called ``optional`` with a value of True, this will wrap given Source in OptionalSource.

The second reserved type if ``binary``. This will encode the ``value`` key with ``encoding`` encoding (default is ascii).

To instantiate the schema, use the following functions:

.. autofunction:: satella.configuration.sources.load_source_from_dict

.. autofunction:: satella.configuration.sources.load_source_from_list
