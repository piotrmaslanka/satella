# v2.7.38

* added context manager to SelfClosingGenerator
* fixed `HashableWrapper`
* fixed the bug in `MemoryPressureManager` where amount 
  of entries into a zone would be counted wrong
* removed __slots__ from classes which inherited from 
  `TerminableThread` since it was pointless