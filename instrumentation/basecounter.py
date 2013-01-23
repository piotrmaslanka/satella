class InstrumentationCounter(object):
    """
    Base class for all instrumentation counters.
    You may want to extend all of those. 
    """

    def __init__(self, name, severity=0):
        """
        Initializes the counter. Counter starts enabled.

        @param name: Name of the instrumentation counter
        @type name: str

        @param severity: Threshold level for usage in limiting information amount.
            This can be used to disable many counters at once - those that are 
            below given threshold
        @type severity: int        
        """
        self.name = name
        self.enabled = True
        self.severity = severity

    def enable(self):
        """Called when this counter should accept data inputted"""
        self.enabled = True

    def disable(self):
        """Called when this counter should stop accepting data inputted"""
        self.enabled = False

    def _on_added(self, insmgr):
        """
        Called when this counter is added to an InstrumentationManager

        @param insmgr: Manager this counter is added to
        @type insmgr: descendant of L{satella.instrumentation.base.InstrumentationManager}
        """
        pass

    def _on_removed(self):
        """Called when this counter is removed from an InstrumentationManager"""
        pass

    def update(self):
        """
        Assigns a new value to given counter.

        It may require none to multiple arguments, depending on exact type of the counter
        """

    def get_current(self):
        """
        Returns current value.

        What it returns will differ depending on the counter.

        Throws L{satella.instrumentation.exceptions.NoDataException} if there's no NoDataException
        available
        """
        return None