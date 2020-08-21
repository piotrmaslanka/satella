==========
Predicates
==========

Predicates are functions that take something and return a boolean about truthfulness
of given statement. Satella contains a bunch of functions to produce these predicates.

Predicates
----------

.. autofunction:: satella.coding.predicates.between

.. autofunction:: satella.coding.predicates.length_is

.. autofunction:: satella.coding.predicates.length_multiple_of

.. autofunction:: satella.coding.predicates.one_of

.. autofunction:: satella.coding.predicates.equals

.. autofunction:: satella.coding.predicates.length_less_than

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

.. autofunction:: satella.coding.predicates.attribute

.. autofunction:: satella.coding.predicates.item
