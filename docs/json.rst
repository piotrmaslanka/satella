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
    :members:
