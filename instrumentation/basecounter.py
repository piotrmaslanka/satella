
class CounterObject(object):
    """
    Base counter object. Namespaces and counters subclass it.

    You need this if you are making custom extensions to instrumentation
    infrastructure. If you just want to make a new counter, inherit 
    from L{Counter} instead.
    """
    def __init__(self, name, description=None):
        """
        Initializes the object
        @param name: Name of the object
        @type name: str
        """
        self.name = name
        self.enabled = True
        self.description = description  #: human-readable description of the value        

    def enable(self):
        """Enable the object"""
        self.enabled = True

    def disable(self):
        """Disable the object"""
        self.enabled = False

    def _on_added(self, insmgr):
        """
        Called when this counter is added to a namespace as a child. Called
        by the adding namespace.

        @param insmgr: Manager this counter is added to
        @type insmgr: descendant of L{satella.instrumentation.CounterCollection}
        """
        pass

    def _on_removed(self):
        """Called when this counter is removed from a namespace"""
        pass

class Counter(CounterObject):
    """
    Base class for all instrumentation counters.
    You may want to OVERRIDE all of following methods
    """

    def __init__(self, name, units=None, description=None):
        """
        Initializes the counter. Counter starts enabled.

        @param name: Name of the instrumentation counter
        @type name: str        
        """
        CounterObject.__init__(self, name, description=description)
        self.units = units   #: in what units is the value expressed

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