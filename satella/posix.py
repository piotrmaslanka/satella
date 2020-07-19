import warnings

from .os import daemonize, PIDFileLock, hang_until_sig, suicide, is_running_as_root

warnings.warn('Importing from satella.posix is deprecated and will be removed in Satella 3.0, '
              'import from satella.os instead', DeprecationWarning)

__all__ = [
    'daemonize',
    'PIDFileLock', 'hang_until_sig',
    'suicide', 'is_running_as_root'
]
