class InstrumentationCounter(object):
    """
    Base class for all instrumentation counters.
    You may want to extend all of those. 
    """

    def __init__(self, name):
        """
        Initializes the counter. Counter starts enabled.

        @param name: Name of the instrumentation counter
        @type name: str
        """
        self.name = name
        self.enabled = True

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

    def _on_remove(self):
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