from satella.channels import LockSignalledChannel, DataNotAvailable, ChannelFailure, ChannelClosed
from satella.channels.sockets import Socket, ServerSocket

from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread
from time import sleep

import unittest

class SocketsTest(unittest.TestCase):
    """Tests for socket class"""

    def test_conn_null_read(self):
        sck = socket(AF_INET, SOCK_STREAM)
        sck.connect(('www.onet.pl', 80))
        sck = Socket(sck)

        sck.write('GET / HTTP/1.0\r\n\r\n')

        self.assertEquals(sck.read(4), 'HTTP')
        self.assertRaises(ChannelClosed, sck.read, 10000)    # I expect HTTP 302: Moved Temporarily
        sck.close()     # this shouldn't throw despite the channel is closed already


    def test_blocking_server(self):
        sck = socket(AF_INET, SOCK_STREAM)
        sck.bind(('127.0.0.1', 50000))
        sck.listen(10)
        sck = ServerSocket(sck)

        class ClientSocketThread(Thread):
            def run(self):
                sleep(0.5)
                sck = socket(AF_INET, SOCK_STREAM)
                sck.connect(('127.0.0.1', 50000))
                sck = Socket(sck)
                sck.write('Hello World')
                self.data = sck.read(3)
                sck.close()

        cs = ClientSocketThread()
        cs.start()

        csk = Socket(sck.read()[0])
        self.assertEquals(csk.read(11), 'Hello World')
        csk.write('Yes')
        csk.close()
        cs.join()
        self.assertEquals(cs.data, 'Yes')
        sck.close()
