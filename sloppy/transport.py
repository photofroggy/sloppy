''' sloppy.transport - photofroggy
    Default transports and base.
'''
from sloppy.flow import ConnectionFactory


class Transport(object):
    """
    Transport objects are wrappers for socket objects.
    
    Different transport objects should be capable of different things.
    """
    
    conn = None
    addr = None
    port = None
    factory = None
    
    def __init__(self, addr, port, factory=None, *args, **kwargs):
        """
        Create a transport.
        """
        self.addr = addr
        self.port = port
        self.factory = factory or ConnectionFactory
        self.init(addr, port, factory, *args, **kwargs)
    
    def init(self, addr, port, factory=None, *args, **kwargs):
        """
        Child classes should override this method to do stuff when the object
        is created.
        """
    
    def protocol(self):
        """
        Create a protocol object for the connection.
        """
        return self.factory.protocol()
    
    def connect(self):
        """
        Open a connection.
        
        Returns `None` on success, error on failure.
        """
        raise NotImplementedError
    
    def write(self, data):
        """
        Write data to the transport.
        
        Return the number of bytes written to the connection.
        """
        return 0
    
    def close(self):
        """
        Close connection.
        """
        raise NotImplementedError
    
    def closed(self, reason):
        """
        Connection has been closed and removed from the main loop.
        """
        raise self.factory.closed(self, reason)
    
    def read(self, bytes=0):
        """
        Read some data from the connection.
        
        This method should return `None` when no data is read from the socket.
        If an error occurs, return an object detailing the error. If the socket
        has been closed, then the method should return `False`. Otherwise,
        return the raw data read from the socket.
        
        If the transport is serving a port, then this method should return
        a `Transport` object for a newly established connection.
        """
        raise NotImplementedError


class TCPClient(Transport):
    """
    TCP client transport.
    
    This object connects to a server using a TCP socket, and provides methods
    to read and write data on the socket.
    """
    
    def connect(self):
        """
        Open a connection.
        
        Returns `None` on success, error on failure.
        """
        self.factory.starting()
        self.conn = None
        
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect((socket.gethostbyname(self.addr), self.port))
            self.conn.setblocking(0)
            self.conn.settimeout(.5)
        except socket.error as e:
            self.conn = None
            self.factory.fail(self, e)
            return False
        
        self.factory.connected(self)
        return True
    
    def write(self, data):
        """
        Write some data to the connection.
        
        Returns the number of bytes written to the connection.
        """
        if self.conn is None:
            return 0
        
        try:
            sent = self.conn.send( data )
            return sent
        except socket.error:
            return -1
    
    def close(self):
        """
        Close the connection.
        """
        try:
            self.conn.close()
        except socket.error:
            pass
        self.conn = None
    
    def read(self, bytes=0):
        """
        Read some data from the connection.
        
        This method returns `None` when there is no data to read from the
        socket. If an error occurs, this method returns an object detailing the
        error. If the socket has been closed, then the method returns `False`.
        Otherwise, the raw data read from the socket is returned.
        """
        data = None
        
        try:
            data = self.conn.recv(bytes)
        except socket.error as e:
            if ((e.args[0] == 'timed out')
                or (e.args[0] == errno.EAGAIN)
                or (os.name == 'nt' and e.args[0] == errno.WSAEWOULDBLOCK)
                or (e.args[0] == errno.EINTR)):
                    return None
            elif self.conn and e.args[0]:
                return e
        
        return data or False


class TCPServer(Transport):
    """
    TCP server object.
    
    This transport provides functionality allowing applications to serve
    requests on a port. The object creates new TCPClient objects for new
    connections received, and passes these objects to the application loop.
    """
    
    def __init__(self, addr, port, factory=None, transport=None, *args, **kwargs):
        """
        Create a transport.
        """
        self.addr = addr
        self.port = port
        self.factory = factory or ConnectionFactory
        self._transport = transport or TCPClient
        self.init(addr, port, factory, transport, *args, **kwargs)
    
    def connect(self):
        """
        Start serving requests on the port specified when creating the object.
        """
        self.factory.starting()
        self.conn = None
        
        try:
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.bind((socket.gethostbyname(self.addr), self.port))
            self.conn.setblocking(0)
            self.conn.settimeout(.5)
            self.conn.listen(5)
        except socket.error as e:
            self.conn = None
            self.factory.fail(self, e)
            return False
        
        self.factory.connected(self)
        return True
    
    def close(self):
        """
        Stop serving requests.
        """
        try:
            self.conn.close()
        except socket.error:
            pass
        self.conn = None
    
    def read(self, bytes=0):
        """
        Accept an incoming connection.
        
        This method accepts connections instead of reading data, as this
        transport is used for serving a port on a server.
        """
        incoming, addr = self.conn.accept()
        transport = self._transport(addr, self.port, self.factory)
        transport.conn = incoming
        return transport

