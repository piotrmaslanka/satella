from ssl import SSLError

from satella.network.exceptions import ConnectionFailedException
from satella.network.socket import BaseSocket


class SSLBaseSocket(BaseSocket):
    """Basic wrapper around a SSL-wrapped socket"""
    def on_read(self):
        try:
            BaseSocket.on_read(self)
        except SSLError:
            raise ConnectionFailedException, 'SSLError raised'

    def on_write(self):
        try:
            BaseSocket.on_write(self):
        except SSLError:
            raise ConnectionFailedException, 'SSLError raised'
