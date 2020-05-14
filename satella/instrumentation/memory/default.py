from .memthread import MemoryPressureManager
import gc


def install_force_gc_collect(severity_level: int = 1) -> None:
    """
    Install a default first severity level handler that forces a GC collection

    :param severity_level: severity level on which to call
    """
    MemoryPressureManager().register_on_entered_severity(severity_level)(gc.collect)
