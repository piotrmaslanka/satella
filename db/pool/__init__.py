import Queue

class DatabaseDefinition(object):
    def __init__(self, cccall, cbexcepts, cccall_args=(), cccall_kwargs={}, xwcb=lambda e: True, acs=lambda x: None):
        """
        @param cccall: A callable that can produce Connection objects
        @param cbexcepts: Array of exception types that signify that connection was broken
        @type cbexcepts: tuple or list of exceptions, or else a single exception type.
        @param cccall_args: Array of arguments to pass to cccall as *args
        @param cccall_kwargs: Dictionary of arguments to pass to cccall as **kwargs
        @param xwcb: If the database layer throws an exception, and it's type belongs to
            cbexcepts, this callable/1 will be called with exception instance as parameter.
            It is to return True if this indeed was the case that connection was broken. This
            can be used to discern if disconnection signalling is more complex that an exception
            of given type. If xwcb return False, the exception will be reraised.
        @param acs: callable that accepts connection as a parameter and performs extra operations on it.
            What it returns doesn't matter.

            For example if you needed an autocommit psycopg2 connection you could do:

                def acs(c): c.autocommit = True
                dd = DatabaseDefinition(psycopg2.connect, ..., ..., ..., ..., acs)

        @type acs: callable/1
        """
        if type(cbexcepts) in (tuple, list):
            self.cb_excepts = tuple(cbexcepts)
        else:
            self.cb_excepts = (cbexcepts, )

        self.xwcb = xwcb
        self.acs = acs
        self.conn_lambda = lambda: cccall(*cccall_args, **cccall_kwargs) #: closure that returns a connection

    def get_connection(self):
        """Returns a new connection object"""
        c = self.conn_lambda()
        self.acs(c)
        return c

class ConnectionPool(object):
    def __init__(self, dd, connections=1):
        """
        @param dd: database definition which will make the connections
        @type dd: L{DatabaseDefinition}
        @param connections: Amount of connections to hold at ready
        @type connections: int
        """
        self.c_num = connections    #: Number of connections
        self.dd = dd                #: DatabaseDefinition object

        self.connections = Queue.Queue()

        for i in xrange(0, connections):
            self.connections.put(self.dd.get_connection())

    def close(self):
        """Closes all connections in this connection pool.
        Use only when you are sure that no-one is using the
        connection pool anymore"""
        while True:
            try:
                k = self.connections.get(False)
            except Queue.Empty:
                break
            k.close()

    def get_connection(self):
        """Gets a connection from the pool. May block
        @return: a connection object"""
        return self.connections.get(True)

    def put_connection(self, conn):
        """Returns a used connection to the pool. May block.
        Connection may be invalid - it will be regenerated next time"""
        self.connections.put(conn)

    def invalidate_connection(self, conn):
        """
        Marks off a connection as invalid. It will not be given
        via get_connection() anymore.

        @param conn: connection object to be considered invalidated
        """
        conn.close()
        self.connections.put(self.dd.get_connection())

    def cursor(self):
        """
        Returns a new cursor, constructed from a connection picked from the pool. 

        If this cursor does a query and it fails (disconnect) it will repeat that again.

        For how disconnection is determined, refer to L{DatabaseDefinition} documentation.

        Do not use this cursor when multiple execute() will comprise a single transaction. If
        a connection fails in the middle, it will be reestablished and you will end up splitting
        your single transaction into two transactions. Mayhem will ensue.
        Preferably use this cursor with "autocommit" connections.

        Use it like that:

            cp = ConnectionPool(some_db_definition, some_connection_amount)
            with cp.cursor() as cur:
                cur.execute('DO SQL')
            # at this point cursor gets closed and underlying connection is 
            # returned to the pool.
        """

        class Cursor(object):
            """
            Cursor wrapper object. Provides automatic reconnect on failed
            execute().

            Supports the context manager protocol.
            """
            def __init__(self, cp):
                """
                Initializes the cursor wrapper.

                Cursor will close() itself on destructor if not closed
                by that time.

                @param cp: master L{ConnectionPool} object
                @type: L{ConnectionPool}
                """
                self.cp = cp
                self.conn = self.cp.get_connection()
                self.cursor = self.conn.cursor()
                self.cleaned_up = False

            def __reconnect(self):
                """Regenerates internal connection and cursor"""
                self.cp.invalidate_connection(self.conn)
                self.conn = cp.get_connection()
                self.cursor = self.conn.cursor()

            def close(self):
                """Closes the cursor, returns the connection.
                to the pool"""
                self.cursor.close()
                self.cp.put_connection(self.conn)
                self.cleaned_up = True

            def __del__(self):
                if not self.cleaned_up: self.close()

            def __enter__(self):
                return self

            def __exit__(self, type, value, traceback):
                self.close()
                return False

            def execute(self, *args, **kwargs):
                while True:
                    try:
                        self.cursor.execute(*args, **kwargs)
                    except self.cp.dd.cb_excepts as exc:
                        if not self.cp.dd.xwcb(exc): raise
                        self.__reconnect()
                        continue
                    break

            def executemany(self, *args, **kwargs):
                while True:
                    try:
                        self.cursor.executemany(*args, **kwargs)
                    except self.cp.dd.cb_excepts as exc:
                        if not self.cp.dd.xwcb(exc): raise
                        self.__reconnect()
                        continue
                    break

            def __getattr__(self, name):
                return getattr(self.cursor, name)

        return Cursor(self)