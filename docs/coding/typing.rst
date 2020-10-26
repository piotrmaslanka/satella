Typing
======

Satella contains some expressions to help you with typing.
You import them from `satella.coding.typing`.
They are as follows:

* `ExceptionClassType` - base type of exception class
* `Number` - an amalgam of int and float
* `T`, `U`, `K`, `V` - type vars to use
* `Iteratable` - a generic iterator or an iterable of `T`
* `NoArgCallable` - a callable with no arguments returning `T`
* `Appendable` - an object which has the `append` method
* `Predicate` - a callable that accepts a `T` and returns a bool

You may use these generics in your classes, eg.

::

    def enumerate(v: Iteratable[int]) -> int:
        ...


