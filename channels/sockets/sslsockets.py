from satella.channels.sockets.sockets import Socket, ServerSocket
from satella.channels.exceptions import ChannelFailure, DataNotAvailable

from ssl import SSLError

class SSLSocket(Socket):
    def read(self, *args, **kwargs):
        try:
            return Socket.read(self, *args, **kwargs)
        except SSLError:
            self.close()
            raise ChannelFailure, 'SSL failure'

    def write(self, *args, **kwargs):
        try:
            return Socket.write(self, *args, **kwargs)
        except SSLError:
            self.close()
            raise ChannelFailure, 'SSL failure'


class SSLServerSocket(ServerSocket):
    def __init__(self, socket):
        """@type socket: SSL-wrapped server socket"""
        ServerSocket.__init__(self, socket)

    def read(self):
        try:
            # try to accept it and repack it into a SSLSocket channel
            return SSLSocket(ServerSocket.read(self).get_underlying_object())
        except SSLError:
            raise DataNotAvailable, 'SSL failure'
