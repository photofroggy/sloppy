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


class Protocol(object):
    
    def connected(self, transport):
        """
        Called when a connection is established.
        """
    
    def data_received(self, data):
        """
        Called when data is received on the connection.
        """
    
    def connection_closed(self, reason):
        """
        Called when the connection has been closed.
        """
    
