# Typechecking

Satella typechecking is a complex solution for:
* extracting callable arguments signature
* checking type compatibility at runtime

If you do `@typed` on a class method, skip the type of self or cls, since Satella will
detect that it's annotating a class method.