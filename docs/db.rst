Python DB API 2
===============

However imperfect may it be, it's here to stay.

So enjoy!

.. autoclass:: satella.db.transaction
    :members:

You might use is also a context decorator, eg.

>>> @transaction(conn)
>>>    def do_transaction():