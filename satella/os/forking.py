from satella.coding.concurrent import CallableGroup

notify_fork_before = CallableGroup()
notify_fork_after_child = CallableGroup()
notify_fork_after_parent = CallableGroup()
