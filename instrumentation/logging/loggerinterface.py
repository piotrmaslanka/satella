class LoggerInterface(object):
    """Interface for logger classes"""

    def specialize_tag(self, tag):
        """
        Return a new class with logger interface.
        The child class will log all events to parent
        logger, save for the fact that each entry will
        have 'tag' added to list of tags.

        @param tag: tag that will be added to each entry
        @type tag: str
        @return: L{LoggerInterface} implementation instance
        """
        raise RuntimeError, 'abstract'

    def specialize_hierarchy(self, h):
        """
        Return a new class with logger interface.
        The child class will log all events to parent
        logger, save for the fact that each entry will
        have 'h' prepended to hierarchy (along with the
        needed dot - or not if logged hierarchy is empty)

        @param tag: tag that will be added to each entry
        @type tag: str
        @return: L{LoggerInterface} implementation instance        
        """
        raise RuntimeError, 'abstract'


    def _get_entry(self, *args, **kwargs):
        """The helper to .log() that outputs a LogEntry
        object from parameters"""

    def log(self, *args, **kwargs):
        """
        Invoke appropriate LogEntry constructor with 
        *args and **kwargs. How this is parsed is totally
        dependent on the implementation - make it so that
        actually _USING_ it with your program is simple.

        Relay the log onto suitable logging backend.
        """
        raise RuntimeError, 'abstract'        