from satella.channels import LockSignalledChannel, DataNotAvailable, ChannelFailure, ChannelClosed
from satella.channels.sockets import SSLSocket, SSLServerSocket, SelectHandlingLayer, ServerSocket

from satella.channels.unittests.utils import get_dummy_cert

import ssl

from socket import AF_INET, SOCK_STREAM, socket, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
from time import sleep, time

import unittest

TESTING_PORT = 49998

class SSLSelectHandlingLayerTest(unittest.TestCase):
    def test_3_clients(self):
        class ConnectorThread(Thread):
            def __init__(self, utc):
                Thread.__init__(self)
                self.utc = utc
            def run(self):
                sleep(0.2)
                sck = socket(AF_INET, SOCK_STREAM)
                sck = ssl.wrap_socket(sck)
                sck.connect(('127.0.0.1', TESTING_PORT))
                sck = SSLSocket(sck)
                sck.write('Hello World')
                self.utc.assertEquals(sck.read(1), '1')
                self.utc.assertEquals(sck.read(1), '2')
                sck.close()

        class MySelectHandlingLayer(SelectHandlingLayer):
            def __init__(self, utc):
                SelectHandlingLayer.__init__(self)
                self.packets_to_go = 3
                self.sockets_to_close = 3
                self.utc = utc
                self.can_iterate = False

            def on_closed(self, channel):
                self.sockets_to_close -= 1

            def on_readable(self, channel):
                if isinstance(channel, ServerSocket):
                    self.register_channel(channel.read())
                else:
                    if len(channel.rx_buffer) < 11: return
                    self.utc.assertEquals(channel.read(6), 'Hello ')
                    self.utc.assertEquals(channel.read(5), 'World')
                    self.packets_to_go -= 1
                    channel.write('12')

        
        shl = MySelectHandlingLayer(self)

        sck = socket(AF_INET, SOCK_STREAM)
        sck.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        with get_dummy_cert() as dncert:
            sck.bind(('127.0.0.1', TESTING_PORT))
            sck.listen(10)
            sck = ssl.wrap_socket(sck, certfile=dncert)

            shl.register_channel(SSLServerSocket(sck))

            for x in xrange(0, 3): ConnectorThread(self).start()

            test_started_on = time()
            while (shl.packets_to_go != 0) or (shl.sockets_to_close != 0):
                shl.select()
                if (time() - test_started_on) > 20:
                    raise Exception, 'This test is taking too long'

        sck.close()


class SSLSocketsTest(unittest.TestCase):
    """Tests for socket class"""

    def test_blocking_server_client_with_less(self):
        """tests less=True mechanism for channels in sockets"""
        sck = socket(AF_INET, SOCK_STREAM)
        sck.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        with get_dummy_cert() as dncert:
            sck.bind(('127.0.0.1', TESTING_PORT))
            sck.listen(10)
            sck = ssl.wrap_socket(sck, certfile=dncert)
            sck = SSLServerSocket(sck)

            class ClientSocketThread(Thread):
                def __init__(self, utc):
                    Thread.__init__(self)
                    self.utc = utc

                def run(self):
                    """@param utc: unit test class"""
                    sleep(0.1)
                    sck = socket(AF_INET, SOCK_STREAM)
                    sck = ssl.wrap_socket(sck)
                    sck.connect(('127.0.0.1', TESTING_PORT))
                    sck = SSLSocket(sck)
                    pkdata = sck.read(100, less=True, peek=True)
                    data = sck.read(100, less=True)
                    self.utc.assertEquals(pkdata, 'Long string? Not enough.')
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
        sck.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        with get_dummy_cert() as dncert:
            sck.bind(('127.0.0.1', TESTING_PORT))
            sck.listen(10)
            sck = ssl.wrap_socket(sck, certfile=dncert)
            sck = SSLServerSocket(sck)

            class ClientSocketThread(Thread):
                def __init__(self, utc):
                    Thread.__init__(self)
                    self.utc = utc

                def run(self):
                    """@param utc: unit test class"""
                    sleep(0.1)
                    sck = socket(AF_INET, SOCK_STREAM)
                    sck = ssl.wrap_socket(sck)
                    sck.connect(('127.0.0.1', TESTING_PORT))
                    sck = SSLSocket(sck)
                    sck.write('Hello World')
                    self.pkdata = sck.read(3, less=False, peek=True)
                    self.data = sck.read(1)
                    self.data2 = sck.read(2)
                    self.utc.assertRaises(ChannelClosed, sck.read, 1)
                    sck.close()

            cs = ClientSocketThread(self)
            cs.start()

            csk = sck.read()
            self.assertEquals(csk.read(5), 'Hello')
            self.assertEquals(csk.read(6), ' World')
            csk.write('Yes')
            csk.close()
            cs.join()
            self.assertEquals(cs.pkdata, 'Yes')
            self.assertEquals(cs.data, 'Y')
            self.assertEquals(cs.data2, 'es')
            sck.close()
