==========
Predicates
==========

By a predicate Satella understands a function of a single argument and a single return values.
Satella's API drastically simplifies writing lambda.

Satella lets you express lambdas in a Pythonic way, eg:

    ::

        p = x == 2

        assert(p(2) and not p(1))

        p = x > 2

        assert(p(2) and not p(1))


This behaviour extends to operators, item procurement and attr procurement.
The only exceptions are operator subject to Python limitations (ie.
__len__ being allowed to return an int only for example) is called.

These are mentioned in the docs below.

You can also piece together multiple predicates.
Because of Python limitations please use & and | operators in place of and and or.
Also use ^ in place of xor and ~ in place of not.


    ::

        p = x > 2 & x < 6

        assert(p(4) and not p(8) and not p(1))

PredicateClass class is documented here:

.. autoclass:: satella.coding.predicates.PredicateClass
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


Only take care for x to be the first argument in all operators you use. For example,
don't do this:

    ::

        p = 2 < x < 6


Because Python will compare first 2 with x using int's __gt__, which will fail.

If you specify a structure, using predicates, say:

::
    struct = [(x, x*2)]

Then to get the corresponding {2: 4} you can use:

::
    a = build_structure(struct, 2, dict)
    assert a == {2: 4}

