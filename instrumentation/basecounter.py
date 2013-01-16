class InstrumentationCounter(object):
    """
    Base class for all instrumentation counters
    """

    def __init__(self, name):
        """
        @param name: Name of the instrumentation counter
        @type name: str
        """
        self.name = name

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