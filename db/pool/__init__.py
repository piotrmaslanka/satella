import Queue

class DatabaseDefinition(object):
    def __init__(self, cccall, cbexcepts, cccall_args=(), cccall_kwargs={}, 
                 xwcb=lambda e: True, acs=lambda x: None, occ=lambda x: None,
                 oct=lambda x: None, integ_err_cls=(None, None)):
        """

        This initializes a database definition. Because different databases work
        differently, you may want to read this in it's entirety in order to better
        understand what to type.

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
        @param occ: callable that accepts a freshly created cursor via .cursor() to execute some 
            operations on it. What it returns doesn't matter.
        @type occ: callable/1
        @param oct: callable that accepts a freshly created cursor via .transaction() to execute some
            operations on it. What it returns doesn't matter.

            For example, you may want to begin a transaction, because MySQL does not implicitly start them
            unless set with autocommit:

            def oct(c): c.execute('START TRANSACTION')
            dd = DatabaseDefinition(psycopg2.connect, ..., ..., ..., ..., ..., ...., oct)

            Some better-behaved databases do, and in that case you may wish to leave this parameter
            at it's default.

        @type oct: callable/1
        @param integ_err_cls: tuple of A, B. If .execute() throws an 
            exception of this class A, it will be rethrown as B (raise B)
        @type integ_err_cls: tuple of (class, class)
        """
        if type(cbexcepts) in (tuple, list):
            self.cb_excepts = tuple(cbexcepts)
        else:
            self.cb_excepts = (cbexcepts, )

        self.xwcb = xwcb
        self.acs = acs
        self.occ = occ
        self.oct = oct
        self.conn_lambda = lambda: cccall(*cccall_args, **cccall_kwargs) #: closure that returns a connection
        self.integ_err_cls = integ_err_cls

    def get_connection(self):
        """Returns a new connection object. This connects to the database with according
        definitions from L{DatabaseDefinition} passed at constructor."""
        c = self.conn_lambda()
        self.acs(c)
        return c

class ConnectionPool(object):
    """
    Provides .cursor() and .transaction() calls, which returns cursors that can be used as normal
    DB API cursors. Most importantly, they support the context manager ("with") protocol, and using
    them with that is EXPECTED.

    They both .commit() when context is left without an exception, and .rollback() if it's left
    with an exception. Context managers never swallow exceptions.

    Use .cursor() if you have an autocommit connection and don't care about transactionism.
    Use .transaction() if in a single context you do a single transaction and you need all
    the proper behaviour you can get.
    """

    class CursorWrapper(object):
        """
        A class to inherit from when making custom cursor wrappers.
        This is utilized by .cursor() and .transaction()
        """
        def __init__(self, cp, is_transaction):
            """
            @param cp: master L{ConnectionPool} object
            @type: L{ConnectionPool}
            @param is_transaction: Whether this is a transaction or not - to deploy
                appropriate occ or oct
            @type is_transaction: bool
            """
            self.cleaned_up = False
            self.is_transaction = is_transaction

            self.cp = cp
            self.conn = self.cp.get_connection()
            try:
                self.cursor = self.conn.cursor()
            except:
                self._reconnect()
                self.cursor = self.conn.cursor()

            (self.cp.dd.oct if self.is_transaction else self.cp.dd.occ)(self.cursor)

        def _reconnect(self):
            """Regenerates internal connection and cursor"""
            self.cp.invalidate_connection(self.conn)
            self.conn = self.cp.get_connection()
            self.cursor = self.conn.cursor()
            (self.cp.dd.oct if self.is_transaction else self.cp.dd.occ)(self.cursor)

        def __enter__(self):
            return self

        def __exit__(self, type, value, traceback):
            """
            Context manager exit. This does the following:
                - If the wrapper represented a transaction:
                    - If no exception has occurred, COMMIT
                    - If exception has occurred, ROLLBACK
                - Close the cursor
                - Return the connection to the pool
            """
            if self.is_transaction:
                if type == None: # no exception occurred, commit safely
                    self.conn.commit()
                else:
                    self.conn.rollback()
            self.close()
            return False

        def close(self):
            """Closes the cursor, returns the connection.
            to the pool"""
            self.cursor.close()
            self.cp.put_connection(self.conn)
            self.cleaned_up = True

        def __getattr__(self, name):
            """Used so that wrapping can be done right"""
            return getattr(self.cursor, name)            

        def __del__(self):
            """So that if somebody forgets .close() the connection will end up released"""
            if not self.cleaned_up: self.close()

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

    def regenerate_all(self):
        """Sanitize connections. Use it for occassions 
        such as fork() and so on"""
        for i in xrange(0, self.c_num):
            con = self.connections.get()
            con.close()
        for i in xrange(0, self.c_num):
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


    def transaction(self):
        """
        Returns a new cursor. This differs from .cursor() in that disconnect-hardiness
        is tailored specially towards transactions. This assumes that your database opens
        a transaction as soon as a cursor is created. This is false for some borderline
        cases (eg. MySQL), you should use DatabaseDefinition's acs parametr to counter
        that by issuing appropriate behaviour settings.

        General difference between .cursor() and .transaction() is that in .cursor() EVERY execute()
        or executemany() will be retried if it disconnects, whereas in .transaction() only the 
        first call will.        

        DO NOT USE THIS IS THE CONNECTION IS AUTOCOMMITTING.
        """

        class TransactionCursor(self.CursorWrapper):
            """
            Cursor wrapper object. Provides automatic reconnect on failed
            execute().

            Supports the context manager protocol.
            """
            
            class IntegrityError(Exception):
                """Thrown when cursor raises an integrity error"""
            
            def __init__(self, cp):
                """
                Initializes the cursor wrapper.

                Cursor will close() itself on destructor if not closed
                by that time.

                @param cp: master L{ConnectionPool} object
                @type: L{ConnectionPool}
                """                
                super(TransactionCursor, self).__init__(cp, True)
                self.first_query = True

            def execute(self, *args, **kwargs):
                while True:
                    try:
                        self.cursor.execute(*args, **kwargs)
                    except self.cp.dd.cb_excepts as exc:
                        if isinstance(exc, self.cp.dd.integ_err_cls[0]):
                            raise self.cp.dd.integ_err_cls[1]
                        if not self.first_query: raise
                        if not self.cp.dd.xwcb(exc): raise
                        self._reconnect()
                        continue
                    except self.cp.dd.integ_err_cls[0]:
                        raise self.cp.dd.integ_err_cls[1]
                    self.first_query = False
                    break

            def executemany(self, *args, **kwargs):
                while True:
                    try:
                        self.cursor.executemany(*args, **kwargs)
                    except self.cp.dd.cb_excepts as exc:
                        if isinstance(exc, self.cp.dd.integ_err_cls[0]):
                            raise self.cp.dd.integ_err_cls[1]
                        if not self.first_query: raise
                        if not self.cp.dd.xwcb(exc): raise
                        self._reconnect()
                        continue
                    except self.cp.dd.integ_err_cls[0]:
                        raise self.cp.dd.integ_err_cls[1]
                    self.first_query = False
                    break


        return TransactionCursor(self)

    def cursor(self):
        """
        Returns a new cursor, constructed from a connection picked from the pool. 

        If this cursor does a query and it fails (disconnect) it will repeat that again.

        For how disconnection is determined, refer to L{DatabaseDefinition} documentation.

        If you need to have transactions span multiple .execute() calls, consider .transaction()
        instead. .cursor() is best-served if your .execute() and .executemany() are autocommitting,
        if you need them that way then L{DatabaseDefinition} occ and acs are your friends. If it's not
        autocommitting, you may expect rare-case weird behaviour (eg. queries not being committed despite
        .execute() succeeding). DON'T USE THIS IF THE CONNECTION IS NOT AUTOCOMMITTING.

        General difference between .cursor() and .transaction() is that in .cursor() EVERY execute()
        or executemany() will be retried if it disconnects, whereas in .transaction() only the first
        call will.

        Use it like that:

            cp = ConnectionPool(some_db_definition, some_connection_amount)
            with cp.cursor() as cur:
                cur.execute('DO SQL')
                cur.execute('YES PLZ')
            # at this point cursor gets closed and underlying connection is 
            # returned to the pool. 
        """

        class Cursor(self.CursorWrapper):
            """
            Cursor wrapper object. Provides automatic reconnect on failed
            execute().

            Supports the context manager protocol.
            """

            class IntegrityError(Exception):
                """Thrown when cursor raises an integrity error"""            
            
            def __init__(self, cp):
                super(Cursor, self).__init__(cp, False)

            def execute(self, *args, **kwargs):
                while True:
                    try:
                        self.cursor.execute(*args, **kwargs)
                    except self.cp.dd.cb_excepts as exc:
                        if isinstance(exc, self.cp.dd.integ_err_cls[0]):
                            raise self.cp.dd.integ_err_cls[1]
                        if not self.cp.dd.xwcb(exc): raise
                        self._reconnect()
                        continue
                    except self.cp.dd.integ_err_cls[0]:
                        raise self.cp.dd.integ_err_cls[1]
                    break

            def executemany(self, *args, **kwargs):
                while True:
                    try:
                        self.cursor.executemany(*args, **kwargs)
                    except self.cp.dd.cb_excepts as exc:
                        if isinstance(exc, self.cp.dd.integ_err_cls[0]):
                            raise self.cp.dd.integ_err_cls[1]
                        if not self.cp.dd.xwcb(exc): raise
                        self._reconnect()
                        continue
                    except self.cp.dd.integ_err_cls[0]:
                        raise self.cp.dd.integ_err_cls[1]
                    break

        return Cursor(self)