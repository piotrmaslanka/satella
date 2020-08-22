==========
Predicates
==========

Predicates are functions that take something and return a boolean about truthfulness
of given statement. Satella contains a bunch of functions to produce these predicates.

These go superbly hand-in-hand with preconditions and postconditions.

Predicates
----------

.. autofunction:: satella.coding.predicates.between

.. autofunction:: satella.coding.predicates.length_is

.. autofunction:: satella.coding.predicates.length_multiple_of

.. autofunction:: satella.coding.predicates.one_of

.. autofunction:: satella.coding.predicates.equals

.. autofunction:: satella.coding.predicates.shorter_than

.. autofunction:: satella.coding.predicates.longer_than

.. autofunction:: satella.coding.predicates.is_not_none

.. autofunction:: satella.coding.predicates.not_equal

.. autofunction:: satella.coding.predicates.has_keys


Decorators
----------

Decorators are used to extend given predicates. Eg:

    ::
        P = namedtuple('P', ('x', 'y'))
        p = P(2,5)
        assert attribute(equals(5), 'y')(p)

    ::

        p = [1, 2, 5]
        assert item(equals(2), 1)(p)

    ::
        p = [1, 2, 5]
        assert p_all(item(equals(1), 0), item(equals(2), 1))

    ::
        p = [1, 2, 5]
        assert p_any(item(equals(1), 0), item(equals(2), 1))


.. autofunction:: satella.coding.predicates.attribute

.. autofunction:: satella.coding.predicates.item

.. autofunction:: satella.coding.predicates.p_all

.. autofunction:: satella.coding.predicates.p_any
