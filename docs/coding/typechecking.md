# Typechecking

Satella typechecking is a complex solution for:
* extracting callable arguments signature
* checking type compatibility at runtime

If you do `@typed` on a class method, skip the type of self or cls, since Satella will
detect that it's annotating a class method.

## Typechecking instance methods

If you need to use `@typed` for instancemethods, do the following:

```python
class Cheese(object):

    @typed('self', int, int):
    def add_two_ints(self, a, b):
        return a+b
```

## Singleton

If you need to make your class into a singleton, do the following:

```python
from satella.coding import Singleton

@Singleton
class MyClass(object):
    pass
```
