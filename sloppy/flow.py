''' sloppy.flow - photofroggy
    Base classes for controlling program flow.
'''


class ConnectionFactory(object):
    """
    Base interface for any connection factories.
    """
    
    def starting(self):
        """
        We have started to connect, or are just about to. I dunno.
        """
    
    def connected(self, transport):
        """
        Connection opened! Woo!
        """
    
    def protocol(self):
        """
        Create a protocol object for the connection.
        """
        return Protocol()
    
    def fail(self, transport, reason):
        """
        Connection failed.
        """
    
    def closed(self, transport, reason):
        """
        We have lost our connection. Boooo.
        """


class ServerFactory(ConnectionFactory):
    """
    A basic factory that serves connections on a port.
    """
    
    def __init__(self, protocol=None, *args, **kwargs):
        """
        Store the protocol class to be used for connections.
        """
        self._protocol = protocol or Protocol
        self.init(*args, **kwargs)
    
    def init(self, *args, **kwargs):
        """
        Child classes should override this to do stuff on instances.
        """
    
    def protocol(self):
        """
        Return appropriate protocol object.
        """
        return self._protocol()


class Protocol(object):
    
    def connected(self, transport):
        """
        Called when a connection is established.
        """
    
    def on_data(self, data):
        """
        Called when data is received on the connection.
        """
    
    def connection_closed(self, reason):
        """
        Called when the connection has been closed.
        """
    
