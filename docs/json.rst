====
JSON
====

In order to better support JSON, you should declare each of your class that supports being converted to JSON
with

.. autoclass:: satella.json.JSONAble
    :members:

Then you can convert structures made out of standard serializable Python JSON objects, such as dicts
and lists, and also JSONAble objects, by this all

.. autofunction:: satella.json.json_encode

You might also want to check out the JSONEncoder satella uses to do it.

.. autoclass:: satella.json.JSONEncoder

This will serialize unknown objects in the following way.
First, **__dict__** will be extracted out of this object. The dictionary
will be constructed in such a way, that for each key in this **__dict__**,
it's value's **repr** will be assigned.

.. autofunction:: satella.json.read_json_from_file

.. autofunction:: satella.json.write_json_to_file

.. autofunction:: satella.json.write_json_to_file_if_different


