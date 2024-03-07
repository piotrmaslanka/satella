import logging
import os
import typing as tb

from satella.coding.recast_exceptions import rethrow_as
from .base import BaseSource
from .derivative import MergingSource
from .format import FORMAT_SOURCES, FormatSource
from ...coding.typing import Predicate
from ...exceptions import ConfigurationError

logger = logging.getLogger(__name__)

__all__ = ['FileSource', 'DirectorySource']

FormatSourceType = tb.Union[tb.Type[FormatSource], str]


class FileSource(BaseSource):
    """
    Try to read a file and parse it with a known format.
    """
    __slots__ = ('source_classes', 'path', 'encoding')

    def __init__(self, path: str,
                 encoding: str = 'utf-8',
                 interpret_as: tb.List[FormatSourceType] = FORMAT_SOURCES):
        """
        :param interpret_as: names or classes of format sources to parse with
        """
        super().__init__()
        from .. import sources
        self.source_classes = [
            (p if not isinstance(p, str) else getattr(sources, p)) for p in
            interpret_as]        # type: tp.List[tp.Type[FormatSource]]
        self.path = path  # type: str
        self.encoding = encoding  # type: str

    def __repr__(self):
        return '<FileSource %s, %s, ..>' % (repr(self.path), repr(self.encoding))

    @rethrow_as((IOError, OSError), ConfigurationError)
    def provide(self) -> dict:

        with open(self.path, 'rb') as fin:
            data = fin.read()

        for source_class in self.source_classes:
            try:
                s = source_class(data, encoding=self.encoding).provide()
                if not isinstance(s, dict):
                    raise ConfigurationError('%s is not a dict instance' % (s,))
                return s
            except ConfigurationError as e:
                logger.warning('Error processing source %s - %s', self.path, repr(e))
                pass
        else:
            raise ConfigurationError('no reader could parse the file')


class DirectorySource(FileSource):
    """
    Load all files from given directory and merge them


    :param filter: callable that tells whether to use this file (or subdirectory if scan_subdirectories is enabled)
    :param on_fail: what to do in case a resource fails
    """
    __slots__ = ('filter', 'scan_subdirectories', 'on_fail')

    RAISE = MergingSource.RAISE  # in case a resource fails raise it
    SILENT = MergingSource.SILENT  # in case a resource fails silently ignore it

    def __init__(self, path, encoding: str = 'utf-8',
                 interpret_as=FORMAT_SOURCES,
                 fname_filter: Predicate[str] = lambda fullpath: True,
                 scan_subdirectories: bool = True,
                 on_fail: int = RAISE):

        super().__init__(path, encoding, interpret_as)
        self.filter = lambda files: filter(fname_filter,
                                           files)  # type: tp.Callable[[tp.List[str]], tp.List[str]]
        self.scan_subdirectories = scan_subdirectories  # type: bool
        self.on_fail = on_fail  # type: int

    def __repr__(self):
        return '<DirectorySource %s, %s, ..>' % (repr(self.path), repr(self.encoding))

    def get_sources_from_directory(self, directory: str) -> tb.List[FileSource]:

        sources = []  # list of  FileSource

        try:
            files = self.filter(os.path.join(directory, x) for x in os.listdir(directory))
        except OSError as e:
            if self.on_fail == DirectorySource.SILENT:
                logger.warning(
                    'OSError %s while accessing configuration directory %s, skipping files' % (
                        e, directory))
                return []
            else:
                raise ConfigurationError(f'Directory {directory} does not exist')

        for file_name in files:

            fullname = os.path.join(directory, file_name)
            if os.path.isfile(fullname):
                sources.append(FileSource(fullname, encoding=self.encoding,
                                          interpret_as=self.source_classes))
            elif os.path.isdir(fullname) and self.scan_subdirectories:
                sources.extend(self.get_sources_from_directory(fullname))
            else:
                pass  # FIFOs or sockets or something else

        return sources

    def provide(self) -> dict:
        return MergingSource(
            *self.get_sources_from_directory(self.path),
            on_fail=self.on_fail).provide()


try:
    import requests
except ImportError:
    pass
else:
    class HTTPJSONSource(BaseSource):
        """Call somwhere, count on a 200-esque code and return a JSON!"""

        __slots__ = ('url', 'method', 'kwargs')

        def __init__(self, url: str, method: str = 'GET', **kwargs):
            """
            :param kwargs: these will be passed to requests.request(..)
            """
            super(HTTPJSONSource, self).__init__()
            self.url = url  # type: str
            self.method = method  # type: str
            self.kwargs = kwargs  # type: tp.Dict[str, tp.Any]

        @rethrow_as(requests.RequestException, ConfigurationError)
        def provide(self) -> dict:
            r = requests.request(self.method, self.url, **self.kwargs)
            if r.status_code >= 400:
                raise ConfigurationError(
                    'Target responded with HTTP %s' % (r.status_code,))

            return r.json()


    __all__.append('HTTPJSONSource')
