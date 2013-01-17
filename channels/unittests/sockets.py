from satella.channels import LockSignalledChannel, DataNotAvailable, ChannelFailure, ChannelClosed
from satella.channels.sockets import Socket
from socket import AF_INET, SOCK_STREAM, socket

import unittest

class SocketsTest(unittest.TestCase):
    """Tests for socket class"""

    def test_conn_null_read(self):
        sck = socket(AF_INET, SOCK_STREAM)
        sck.connect(('www.onet.pl', 80))
        sck = Socket(sck)

        sck.write('GET / HTTP/1.0\r\n\r\n')

        self.assertRaises(ChannelClosed, sck.read, 10000)    # I expect HTTP 302: Moved Temporarily
        self.assertRaises(ChannelClosed, sck.close)     # previous call closed the channel