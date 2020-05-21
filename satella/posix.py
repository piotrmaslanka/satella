import warnings
from .os import daemonize, PIDFileLock, hang_until_sig, suicide, is_running_as_root

warnings.warn('Importing from satella.posix is deprecated, import from satella.os instead')

__all__ = [
    'daemonize',
    'PIDFileLock', 'hang_until_sig',
    'suicide', 'is_running_as_root'
]
