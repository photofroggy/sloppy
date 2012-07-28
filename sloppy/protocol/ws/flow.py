''' sloppy.protocol.wsc.flow - photofroggy
    WebSocket flow control.
'''
from sloppy.flow import Protocol
from sloppy.flow import ServerFactory
from sloppy.flow import ConnectionFactory
from sloppy.protocol import http


class WebSocketServerFactory(ServerFactory):
    """
    WebSocket server factory.
    
    This factory serves client connections on a server.
    """


class WebSocketServerProtocol(Protocol):
    """
    Base protocol object for WebSocket server connections.
    """
    
    def __init__(self):
        self.handshaked = False
        self._buffer = ''
    
    def data_received(self, data):
        """
        Called when data is received on the connection.
        """
        self._buffer = ''.join(self._buffer, data.decode())
        
        if not '\0' in self._buffer:
            return
        
        if self._buffer.find('\0') == len(self._buffer) - 1:
            data = self._buffer
            self._buffer = ''
        else:
            data = self._buffer.split('\0')
            self._buffer = data[-1]
            data = data[:-1]
        
        for packet in data:
        
            if not self.handshaked:
                request = http.Request(packet)
                # Has to be a GET
                if request.command is None or request.command != 'GET':
                    continue
                # Needs to be at least HTTP/1.1
                if float(request.request_version.split('/')[-1]) < 1.1:
                    continue
                # Should have headers, and we need an upgrade header.
                if not hasattr(request, 'headers') or 'upgrade' not in request.headers:
                    continue
                # Needs to be requesting a WebSocket connection.
                if 'websocket' not in request.headers['upgrade'].lower():
                    continue
    




