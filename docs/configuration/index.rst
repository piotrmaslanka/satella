=============
Configuration
=============

Satella provides a rich functionality to:

1. Load data from particular sources_ (defined using JSON)_
2. Validate_ that config data and standardize it as far as types are concerned (defined using JSON)_

.. _sources: sources.html
.. _Validate: schema.html

You can craft them either out of Python objects at runtime, or load them using an elegant JSON-based schema.

Satella treats your config files as a huge dictionary, at the topmost level,
although you could possibly make them anything you want (including plain strings, although in this case
it would be a plain bother to use Satella for that).
