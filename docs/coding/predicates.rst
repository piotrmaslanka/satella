==========
Predicates
==========

Predicates are functions that take something and return a boolean about truthfulness
of given statement. Satella contains a bunch of functions to produce these predicates.

Satella lets you express predicates in a Pythonic way, eg:

    ::

        p = x == 2

        assert(p(2) and not p(1))

        p = x > 2

        assert(p(2) and not p(1))


This behaviour extends to operators, item procurement and attr procurement. The only exception is the length,
which due to Python limitations (namely __len__ being allowed to return an int only) is called
via it's method .length(), eg:



    ::

        p = x.length() == 2

        assert(p([1, 2]) and not p([3])


You can also piece together multiple predicates.
Because of Python limitations please use & and | operators in place of and and or.
Also use ^ in place of xor and ~ in place of not.


    ::

        p = x > 2 & x < 6

        assert(p(4) and not p(8) and not p(1))

Predicate class is documented here:

.. autoclass:: satella.coding.predicates.Predicate
    :members:

To use the predicate you are to execute the following import:

    ::

        from satella.coding.predicates import x

        p = x == 2

        assert(p(2))

You can also check if a dict has provided keys

::
    a = {'hello': 'hello', 'world': 'world'}
    p = x.has_keys('hello', 'world')
    assert p(a)

Or check whether an instance is of provided type

::
    p = x.instanceof(int)
    assert p(2)
