''' sloppy.protocol.wsc.flow - photofroggy
    WebSocket flow control.
'''
from sloppy.flow import Protocol
from sloppy.flow import ServerFactory
from sloppy.flow import ConnectionFactory
from sloppy.protocol import http
from sloppy.protocol.ws.error import WSHandshakeError


class WebSocketServerFactory(ServerFactory):
    """
    WebSocket server factory.
    
    This factory serves client connections on a server.
    """
    
    def protocol(self):
        """
        Return appropriate protocol object.
        """
        return self._protocol(self)


class WebSocketServerProtocol(Protocol):
    """
    Base protocol object for WebSocket server connections.
    """
    
    def __init__(self, factory):
        self.handshaked = False
        self._buffer = ''
        self._factory = factory
    
    def connected(self, transport):
        """
        A new client has connected to the server.
        
        Store the transport.
        """
        self._transport = transport
    
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
                    self._factory.fail(self._transport,
                        WSHandshakeError('Client sending data without handshaking'))
                    return
                # Needs to be at least HTTP/1.1
                if float(request.request_version.split('/')[-1]) < 1.1:
                    self._factory.fail(self._transport,
                        WSHandshakeError('Incompatible HTTP version'))
                    return
                # Should have headers, and we need an upgrade header.
                if not hasattr(request, 'headers') or 'upgrade' not in request.headers:
                    self._factory.fail(self._transport,
                        WSHandshakeError('No header values given'))
                    return
                # Needs to be requesting a WebSocket connection.
                if 'websocket' not in request.headers['upgrade'].lower():
                    self._factory.fail(self._transport,
                        WSHandshakeError('Invalid Upgrade header'))
                    return
                # Needs to be requesting a connection upgrade.
                if 'connection' not in request.headers or 'upgrade' not in request.headers['connection'].lower():
                    self._factory.fail(self._transport,
                        WSHandshakeError('Invalid Connection header'))
                    return
                # Needs to be using WebSocket protocol version 13.
                if 'sec-websocket-version' not in request.headers or request.headers['sec-websocket-version'] != '13':
                    self._factory.fail(self._transport,
                        WSHandshakeError('Incompatible WebSocket version'))
                    return
                # Needs to provide a key.
                if 'sec-websocket-key' not in request.headers:
                    self._factory.fail(self._transport,
                        WSHandshakeError('No key provided'))
                    return
                
                # Ok, now we let the handshake method take over.
                self.handshake(request)
    
    def on_handshake(self):
        """
        Handshake received.
        """
    




