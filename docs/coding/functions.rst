========================
Functions and decorators
========================

.. autoclass:: satella.coding.expect_exception

.. autofunction:: satella.coding.enum_value

.. autofunction:: satella.coding.contains

.. autoclass:: satella.coding.class_or_instancemethod

.. autofunction:: satella.coding.chain_callables

.. autofunction:: satella.coding.source_to_function

.. autofunction:: satella.coding.call_with_arguments

.. autofunction:: satella.coding.decorators.replace_argument_if

.. autofunction:: satella.coding.get_arguments

.. autofunction:: satella.coding.queue_iterator

.. autofunction:: satella.coding.update_key_if_not_none

.. autofunction:: satella.coding.update_key_if_true

.. autofunction:: satella.coding.update_attr_if_none

.. autofunction:: satella.coding.merge_dicts

.. autofunction:: satella.coding.static_var

.. autofunction:: satella.coding.silence_excs

.. autoclass:: satella.coding.log_exceptions

.. autoclass:: satella.coding.rethrow_as
    :members:

.. autoclass:: satella.coding.reraise_as
    :members:

.. autofunction:: satella.coding.catch_exception

.. autofunction:: satella.coding.raises_exception

Wrapping classes with something
-------------------------------

Sometimes you need to wrap all methods/properties in given class with
a common decorator. Here's the function you can use:

.. autofunction:: satella.coding.wrap_with

In order to more easily construct functions that will wrap properties,
the following was provided:

.. autofunction:: satella.coding.wrap_property

You can also decorate given callables in order not to be wrapped with

.. autofunction:: satella.coding.dont_wrap

Function overloading
--------------------

.. warning:: This is coded for cases where the function prototypes differ significantly, for ex. matches
            only one prototype. For cases where a single call might match multiple prototypes, and if it's
            desired that the implementation tells them apart, this implementation might not be of sufficient complexity.
        Go file a ticket that you cannot use Satella with some implementation. Just type down what kind of implementation
        that was.

.. autoclass:: satella.coding.overload
    :members:

.. autoclass:: satella.coding.TypeSignature
    :members:


DocsFromParent
--------------

.. autofunction:: satella.coding.DocsFromParent

CopyDocsFrom
------------

.. autofunction:: satella.coding.CopyDocsFrom

metaclass_maker
---------------

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

Deep comparison
---------------

To analyze why two objects don't compare the same, you can use the following functions:

.. autofunction:: satella.coding.assert_equal

.. autoclass:: satella.coding.Inequal
    :members:

.. autoclass:: satella.coding.InequalityReason
    :members:
