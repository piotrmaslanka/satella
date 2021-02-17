Typing
======

Satella contains some expressions to help you with typing.
You import them from `satella.coding.typing`.
They are as follows:

* `NoneType` - the type of `None`
* `ExceptionClassType` - base type of exception class
* `Number` - an amalgam of int and float
* `T`, `U`, `K`, `V` - type vars to use
    * Note that `K` must be hashable
* `Iteratable` - a generic iterator or an iterable of `T`
* `NoArgCallable` - a callable with no arguments returning `T`
* `Appendable` - an object which has the `append` method
* `Predicate` - a callable that accepts a `T` and returns a bool
* `KVTuple` - a tuple of (K, V)
* `Comparable` - a class that allows comparison between it's instances
* `ExceptionList` - either a single exception type or a tuple of exception types.
    As used by `except` statement and some satella functions.

You may use these generics in your classes, eg.

::

    def enumerate(v: Iteratable[int]) -> int:
        ...


