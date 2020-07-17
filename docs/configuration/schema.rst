===============================
Configuration schema validation
===============================

As noted in index_, your configuration is mostly supposed to be a dict. To validate your schema,
you should instantiate a Descriptor. Descriptor reflects how your config is nested.

.. _index: index.html

.. autoclass:: satella.configuration.schema.Boolean

.. autoclass:: satella.configuration.schema.Float

.. autoclass:: satella.configuration.schema.Integer

.. autoclass:: satella.configuration.schema.String

.. autoclass:: satella.configuration.schema.IPv4

.. autoclass:: satella.configuration.schema.List

.. autoclass:: satella.configuration.schema.Dict

.. autoclass:: satella.configuration.schema.Caster

Then there is a descriptor that makes it possible for a value to have one of two types:

.. autoclass:: satella.configuration.schema.Union

You can use the following to declare your own descriptors:

.. autoclass:: satella.configuration.schema.Descriptor
    :members:

.. autoclass:: satella.configuration.schema.Regexp

Just remember to decorate them with

.. autofunction:: satella.configuration.schema.register_custom_descriptor

If you want them loadable by the JSON-schema loader.

You use the descriptors by calling them on respective values, eg.

::

    >>> List(Integer())(['1', '2', 3.0])
    [1, 2, 3]


JSON schema
===========

The JSON schema is pretty straightforward. Assuming the top-level is a dict, it contains keys. A key name is the
name of the corresponding key, and value can have two types. Either it is a string, which is a short-hand for a descriptor,
or a dict containing following values:

::

    {
        "type": "string_type",
        "optional": True/False,
        "default": "default_value" - providing this implies optional=True
    }

Note that providing a short-hand, string type is impossible for descriptors that take required arguments.

Available string types are:

* **int** - Integer
* **str** - String
* **list** - List
* **dict** - Dict
* **ipv4** - IPv4
* **any** - Descriptor
* **bool** - Boolean
* **union** - Union
* **caster** - Caster

Lists you define as following

::

    {
        "type": "list",
        "of": {
            ".. descriptor type that this list has to have .."
        }
    }

Unions you define the following

::

    {
        "type": "union",
        "of": [
            ".. descriptor type 1 ..",
            ".. descriptor type 2 .."
            ]
    }

Dicts are more simple. Each key contains the key that should be present in the dict, and value is it's descriptor
- again, either in a short form (if applicable) or a long one (dict with ``type`` key).

You load it using the following function:

.. autofunction:: satella.configuration.schema.descriptor_from_dict

Casters you define as

::

    {
        "type": "caster"
        "cast_to": "name of a built-in or a fully qualified class ID"
    }

If cast_to is not a builtin, it specifies a full path to a class,
which will be loaded using
:func:`satella.imports.import_class`.

Additionally, an extra argument can be specified:

::
    {
        "type": "caster",
        "cast_to": "name of a built-in or a FQ class ID",
        "expr": "y(int(x))"
    }

In which case cast_to will be displayed as a
**y** in expression,
which will be eval()ed, and this value will be
output. The input value will be called **x**.

