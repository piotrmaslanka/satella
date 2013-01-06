from select import select, error as SelectError
from threading import Thread
from Queue import Queue, Empty

from satella.network.sockets import BaseSocket
from satella.network.exceptions import ConnectionFailedException
from satella.threads import BaseThread

class SelectLoop(BaseThread):
    """
    Thread that does a select loop.
    In general, you are expected to subclass it and write methods corresponding to tasks. The loop works like this:

    - when started, invokes on_startup()
    - in infinite loop (unless terminate()d ):
        * calls on_tick()
        * closes timeouted sockets
        * accepts foreign sockets into the loop (via self.send_socket mechanism)
        * select's on the sockets, closing and removing failed ones as necessary
        * dispatches on_read and on_write, accepts connections.
          if those calls throw ConnectionFailedException, they will be closed
    - when terminated, invokes on_cleanup()
    - remaining client sockets are closed. Server socket is NOT CLOSED.

    When a socket is closed, or fails, it is first closed, when it's on_close() method is invoked, and 
    in the end self.on_sock_closed() is called with the offending socket as argument.

    This class runs out of the box, if you don't overload anything, but it won't do anything of interest,
    just accept connections and receive data from sockets.

    This class doesn't do out-of-band data.
    """
    def __init__(self, server_socket):
        self.select_timeout = 5     #: timeout for select
        self.server_socket = server_socket
        self.client_sockets = []        #: satella.network.socket.BaseSocket descendants

        self.external_accepts = Queue()     #: synchronization element used to accept
                                            #: sockets forcibly into the loop
        BaseThread.__init__(self)

    def send_socket(self, sock):
        """Forces this loop to accept a socket as it's own client socket.
        Can be safely executed from other thread contexts.
        @type sock: L{satella.network.socket.BaseSocket} descendants"""
        self.external_accepts.put(sock)

    def on_accept(self, socket, addr):
        """
        Override this.
        @param socket: raw socket object
        @param addr: raw address tuple.

        @return: new L{satella.network.socket.BaseSocket} or None, if socket is to be forgotten
                 (it can be returned later by send_socket)
        """ 
        return BaseSocket(socket)

    def on_startup(self):
        """Override this. Called before the loop starts iterating, in new thread-context"""
        pass

    def on_tick(self):
        """Override this. Called at each iteration"""
        pass

    def on_cleanup(self):
        """Override this. Called when the loop finishes."""
        pass

    def on_sock_closed(self, sock):
        """VIRTUAL. Given socket is removed from the select layer, it has already been on_close()'d"""
        pass

    # Private variables
    def loop(self):     # it's two separate procedures as it allows more fine-grained flow control via return
        self.on_tick()      # Call on_tick()

        # Close timeouted sockets
        for sock in self.client_sockets[:]:
            if sock.has_expired():
                self.client_sockets.remove(sock)
                sock.close()
                sock.on_close()
                self.on_sock_closed(sock)

        while True:         # Accept foreign sockets
            try:
                new_sock = self.external_accepts.get(False)
            except Empty:
                break
            self.client_sockets.append(new_sock)

        try:            # select the sockets
            rs, ws, xs = select(self.client_sockets + [self.server_socket], 
                                [sock for sock in self.client_sockets if sock.wants_to_write()],
                                (),
                                self.select_timeout)
        except (SelectError, ConnectionFailedException): # some socket has died a horrible death
            for cs in self.client_sockets[:]:
                try:
                    select((cs, ), (), (), 0)
                except (SelectError, ConnectionFailedException): # is was this socket
                    cs.close()
                    self.client_sockets.remove(cs)
                    cs.on_close()
                    self.on_sock_closed(cs)
                    return  # repeat the loop
        except Exception as exc:
            print repr(exc)

        # dispatch on_read and on_write
        for sock in ws:     # analyze sockets ready to be written
            try:
                sock.on_write()
            except ConnectionFailedException:
                sock.close()
                self.client_sockets.remove(sock)
                sock.on_close()
                self.on_sock_closed(sock)
                return

        for sock in rs:     # analyze sockets ready to be read
            if sock == self.server_socket:  # accepting
                n_sock = self.on_accept(*sock.accept())
                if n_sock != None: # socket returned
                    self.client_sockets.append(n_sock)
            else:       # just a civilian socket
                try:
                    sock.on_read()
                except ConnectionFailedException:
                    sock.close()
                    self.client_sockets.remove(sock)
                    sock.on_close()
                    self.on_sock_closed(sock)
                    return

    def run(self):
        self.on_startup()
        while not self._terminating: 
            self.loop()
        self.on_cleanup()
        for sock in self.client_sockets:    # Close surviving client sockets
            sock.close()
            sock.on_close()
            self.on_sock_closed(sock)


