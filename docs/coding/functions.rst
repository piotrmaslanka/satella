========================
Functions and decorators
========================

.. autofunction:: satella.coding.merge_dicts

.. autofunction:: satella.coding.static_var

.. autofunction:: satella.coding.silence_excs

.. autoclass:: satella.coding.rethrow_as
    :members:

.. autofunction:: satella.coding.precondition

.. autofunction:: satella.coding.for_argument


Now, give the following type structure:

::

    class MetaA(type):
        pass

    class MetaB(type):
        pass

    class A(metaclass=MetaA):
        pass

    class B(metaclass=MetaB):
        pass

You just can't construct the following class

::

    class C(A,B):
        pass

Without running into `TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases`.

Following function will help with that:

.. autofunction:: satella.coding.metaclass_maker



