class LogEntrySetInterface(object):
    """
    A sequence of .when-ordered log events along with methods to process the stream.

    Implementing this interface allows an application to retrieve events in a backend-agnostic
    manner.
    """

    def events(self):
        """
        Return an iterator that will return events sorted ascending 
        order by .when, and that will return L{LogEntry} objects (or 
        descendants)
        """
        raise RuntimeError, 'abstract'

    def filter(self, **kwargs):
        """
        Filters the result set according to kwargs keys and values.
        Because of how backends may differ, this is expected to minimally implement
        following keys (for kwargs):
        - when__lt   -   .when less than value
        - when__le   -   .when less or equal than value
        - when__gt   -   .when greater than value
        - when__ge   -   .when greater or equal than value
        - who_hierarchy - either .who is equal to value, or if you take away the value
                          from .who, then the first character will be a dot
        - who       -   .who equal to value
        - tags__in   -   intersection of .tags and value is nonempty
        - tags      -   .tags equal to value

        Returns a L{LogSetInterface} implementation that will not include filtered out values
        shall it's .events() be called.

        If an implementation-specified order of .filter() calls or simultaneous kwargs entries
        is not supported, .filter is to raise ValueError.
        """
        raise RuntimeError, 'abstract'

