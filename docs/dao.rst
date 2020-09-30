===
DAO
===

This is for objects that are meant to represent a database entry,
and are lazily loadable.

It's constructor expects identifier and a keyword argument of load_lazy, which will control
when will the object be fetched from DB.

If True, then it will be fetched at constructor time, ie. the constructor will call .refresh().
If False, then it will be fetched when it is first requested, via `must_be_loaded` decorator.

.. autoclass:: satella.dao.Loadable
    :members:

.. autofunction:: satella.dao.must_be_loaded
