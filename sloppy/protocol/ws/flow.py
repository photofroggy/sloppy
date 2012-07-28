''' sloppy.protocol.wsc.flow - photofroggy
    WebSocket flow control.
'''
from sloppy.flow import Protocol
from sloppy.flow import ConnectionFactory
from sloppy.protocol import http


class WebSocketServerFactory(ConnectionFactory):
    """
    WebSocket server factory.
    
    This factory serves client connections on a server.
    """
    
    def __init___(self, protocol=None, *args, **kwargs):
        """
        Store the protocol class to be used for connections.
        """
        self._protocol = protocol or WebSocketServerProtocol
        self.init(*args, **kwargs)
    
    def protocol(self):
        """
        Return appropriate protocol object.
        """
        return self._protocol()


class WebSocketServerProtocol(Protocol):
    """
    Base protocol object for WebSocket server connections.
    """
    
    




