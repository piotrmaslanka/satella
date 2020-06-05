# v2.7.46

* added `dont_check_multiple` to `choose`
* broke down `schema` to multiple directories
* fixed down `recast_exceptions` (?)
* Deprecated casting to target types in `configuration.sources`, as sources module should
  only be concerned with loading the configuration and not actual casting it. Please define
  your casting in `.schema` part.
