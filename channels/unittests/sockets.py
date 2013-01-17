from satella.channels import LockSignalledChannel, DataNotAvailable, ChannelFailure, ChannelClosed
from satella.channels.sockets import Socket, ServerSocket

from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread
from time import sleep

import unittest

class SocketsTest(unittest.TestCase):
    """Tests for socket class"""

    def test_blocking_server_client_with_less(self):
        """tests less=True mechanism for channels in sockets"""
        sck = socket(AF_INET, SOCK_STREAM)
        sck.bind(('127.0.0.1', 50000))
        sck.listen(10)
        sck = ServerSocket(sck)

        class ClientSocketThread(Thread):
            def __init__(self, utc):
                Thread.__init__(self)
                self.utc = utc

            def run(self):
                """@param utc: unit test class"""
                sleep(0.1)
                sck = socket(AF_INET, SOCK_STREAM)
                sck.connect(('127.0.0.1', 50000))
                sck = Socket(sck)
                data = sck.read(100, less=True)
                self.utc.assertEquals(data, 'Long string? Not enough.')
                self.utc.assertRaises(ChannelClosed, sck.read, 1)
                sck.close()

        cs = ClientSocketThread(self)
        cs.start()

        csk = sck.read()        
        csk.write('Long string? Not enough.')
        csk.close()
        cs.join()
        sck.close()


    def test_blocking_server(self):
        """tests L{ServerSocket} and a client L{Socket} in a multithreaded model"""
        sck = socket(AF_INET, SOCK_STREAM)
        sck.bind(('127.0.0.1', 50000))
        sck.listen(10)
        sck = ServerSocket(sck)

        class ClientSocketThread(Thread):
            def __init__(self, utc):
                Thread.__init__(self)
                self.utc = utc

            def run(self):
                """@param utc: unit test class"""
                sleep(0.1)
                sck = socket(AF_INET, SOCK_STREAM)
                sck.connect(('127.0.0.1', 50000))
                sck = Socket(sck)
                sck.write('Hello World')
                self.data = sck.read(3)
                self.utc.assertRaises(ChannelClosed, sck.read, 1)
                sck.close()

        cs = ClientSocketThread(self)
        cs.start()

        csk = sck.read()
        self.assertEquals(csk.read(11), 'Hello World')
        csk.write('Yes')
        csk.close()
        cs.join()
        self.assertEquals(cs.data, 'Yes')
        sck.close()
