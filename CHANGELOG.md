# v2.14.5

* `Closeable` is now in __all__
* `Closeable` has __slots__
* fixed a bug in `PeekableQueue`
* `TerminableThread.safe_sleep` will do the right thing when passed a negative value
* `Closeable` will output a message if you forgot to call the constructor
* fixed handling of enums by `stringify` and `jsonify`
