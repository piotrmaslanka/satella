from satella.channels import LockSignalledChannel, DataNotAvailable, ChannelFailure, ChannelClosed
from satella.channels.sockets import Socket, ServerSocket, SelectHandlingLayer

from socket import AF_INET, SOCK_STREAM, socket, SOL_SOCKET, SO_REUSEADDR
from threading import Thread
from time import sleep, time

import unittest

TESTING_PORT = 49999

class SelectHandlingLayerTest(unittest.TestCase):
    """This suite requires that www.yahoo.com is reachable and 
    connectable via port 80"""

    def test_async_socket_onconnected_called(self):
        """Tests whether socket's on_connected() is called in async configuration"""
        class CheckSocket(Socket):
            def __init__(self, *args, **kwargs):
                self.on_connected_called = False
                Socket.__init__(self, *args, **kwargs)
            def on_connected(self):
                self.on_connected_called = True

        mshl = SelectHandlingLayer()
        sck = CheckSocket(socket(AF_INET, SOCK_STREAM))
        mshl.register_channel(sck)
        sck.connect(('www.yahoo.com', 80))  # that was just nonblocking

        a = time()
        while (time() - a < 30) and (not sck.on_connected_called):
            mshl.select()

        self.assertEquals(sck.on_connected_called, True)

    def test_nonblocking_connect(self):
        class MySelectHandlingLayer(SelectHandlingLayer):
            def __init__(self, utc):
                SelectHandlingLayer.__init__(self)
                self.utc = utc
                self.ok = False

            def on_connected(self, channel):
                # at this point data should have been flushed
                self.ok = True

        mshl = MySelectHandlingLayer(self)
        sck = Socket(socket(AF_INET, SOCK_STREAM))
        mshl.register_channel(sck)
        sck.connect(('www.yahoo.com', 80))  # that was just nonblocking

        a = time()
        while (time() - a < 30) and (not mshl.ok):
            mshl.select()

        self.assertEquals(mshl.ok, True)


    def test_3_clients(self):
        class ConnectorThread(Thread):
            def __init__(self, utc):
                self.utc = utc
                Thread.__init__(self)
            def run(self):
                sleep(0.2)
                sck = Socket(socket(AF_INET, SOCK_STREAM))
                sck.connect(('127.0.0.1', TESTING_PORT))
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

            def on_closed(self, channel):
                # at this point data should have been flushed
                self.utc.assertEquals(len(channel.tx_buffer), 0)                
                self.sockets_to_close -= 1

            def on_readable(self, channel):
                if isinstance(channel, ServerSocket):
                    self.register_channel(channel.read())
                else:
                    self.utc.assertEquals(channel.blocking, False)

                    if len(channel.rx_buffer) < 11: return
                    self.utc.assertEquals(channel.read(6), 'Hello ')
                    self.utc.assertEquals(channel.read(5), 'World')
                    self.packets_to_go -= 1
                    channel.write('12')

        
        shl = MySelectHandlingLayer(self)

        sck = socket(AF_INET, SOCK_STREAM)
        sck.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sck.bind(('127.0.0.1', TESTING_PORT))
        sck.listen(10)

        shl.register_channel(ServerSocket(sck))

        for x in xrange(0, 3): ConnectorThread(self).start()

        test_started_on = time()
        while (shl.packets_to_go != 0) or (shl.sockets_to_close != 0):
            shl.select()

            if (time() - test_started_on) > 20:
                raise Exception, 'This test is taking too long'

        sck.close()

class SocketsTest(unittest.TestCase):
    """Tests for socket class"""

    def test_blocking_server_client_with_less(self):
        """tests less=True mechanism for channels in sockets"""
        sck = socket(AF_INET, SOCK_STREAM)
        sck.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sck.bind(('127.0.0.1', TESTING_PORT))
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
                sck.connect(('127.0.0.1', TESTING_PORT))
                sck = Socket(sck)
                self.utc.assertEquals(sck.blocking, True)
                self.utc.assertEquals(sck.read(1), 'L')
                pkdata = sck.read(100, less=True, peek=True)
                data = sck.read(100, less=True)
                self.utc.assertEquals(pkdata, 'ong string? Not enough.')
                self.utc.assertEquals(data, 'ong string? Not enough.')
                self.utc.assertRaises(ChannelClosed, sck.read, 1)
                sck.close()

        cs = ClientSocketThread(self)
        cs.start()

        csk = sck.read()        
        csk.write('Long string? Not enough.')
        csk.close()
        cs.join()
        sck.close()


    def test_blocking_server_finite_client_timeout(self):
        sck = socket(AF_INET, SOCK_STREAM)
        sck.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sck.bind(('127.0.0.1', TESTING_PORT))
        sck.listen(10)
        sck = ServerSocket(sck)

        class ClientSocketThread(Thread):
            def __init__(self, utc):
                """@param utc: unit test class"""
                Thread.__init__(self)
                self.utc = utc

            def run(self):
                sck = socket(AF_INET, SOCK_STREAM)
                sck.connect(('127.0.0.1', TESTING_PORT))
                sck = Socket(sck)
                sck.settimeout(5)
                self.utc.assertEquals(sck.read(2), 'Ye')
                self.utc.assertEquals(sck.read(1), 's')
                sck.write('Hello World')
                sck.close()

        cs = ClientSocketThread(self)
        cs.start()

        csk = sck.read()
        sleep(3)
        csk.write('Yes')
        self.assertEquals(csk.read(5), 'Hello')
        self.assertEquals(csk.read(6), ' World')
        csk.close()
        cs.join()

        sck.close()

    def test_blocking_server(self):
        """tests L{ServerSocket} and a client L{Socket} in a multithreaded model"""
        sck = socket(AF_INET, SOCK_STREAM)
        sck.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sck.bind(('127.0.0.1', TESTING_PORT))
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
                sck.connect(('127.0.0.1', TESTING_PORT))

                sck = Socket(sck)
                sck.write('Hello World')
                self.pkdata = sck.read(3, less=False, peek=True)
                self.data = sck.read(3)
                self.utc.assertRaises(ChannelClosed, sck.read, 1)
                sck.close()

        cs = ClientSocketThread(self)
        cs.start()


        csk = sck.read()
        self.assertEquals(csk.read(6), 'Hello ')
        self.assertEquals(csk.read(5), 'World')
        csk.write('Yes')
        csk.close()
        cs.join()
        self.assertEquals(cs.pkdata, 'Yes')
        self.assertEquals(cs.data, 'Yes')
        sck.close()

    def test_reassignment(self):
        """Tests creating a satella socket from a satella socket
        instead of a native socket"""
        sck = socket(AF_INET, SOCK_STREAM)
        sock = Socket(sck)
        sock = Socket(sock)
        self.assertEquals(sock.socket, sck)