# v2.14.29

* `ComparableEnum` will now correctly disassemble other enums
* added `contains`
* fixed a bug in `ComparableEnum` that would ValueError instead of returning
    False when an unknown element of the enum was compared against it
