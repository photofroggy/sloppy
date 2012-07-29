''' sloppy.protocol.wsc.flow - photofroggy
    WebSocket flow control.
'''
import struct
from sloppy.flow import Protocol
from sloppy.flow import ServerFactory
from sloppy.flow import ConnectionFactory
from sloppy.protocol import http
from sloppy.protocol.ws import STATE
from sloppy.protocol.ws.error import WSHandshakeError


# WebSocket frame structs.
STRUCT_BB = struct.Struct("BB")
STRUCT_BBH = struct.Struct("!BBH")
STRUCT_BBQ = struct.Struct("!BBQ")
STRUCT_H = struct.Struct("!H")
STRUCT_Q = struct.Struct("!Q")


class WebSocketServerFactory(ServerFactory):
    """
    WebSocket server factory.
    
    This factory serves client connections on a server.
    """
    
    def protocol(self):
        """
        Return appropriate protocol object.
        """
        #print self._protocol.__name__
        return self._protocol(self)


class WebSocketServerProtocol(Protocol):
    """
    Base protocol object for WebSocket server connections.
    """
    
    def __init__(self, factory):
        self._buffer = ''
        self._frame = None
        #self._factory = factory
    
    def connected(self, transport):
        """
        A new client has connected to the server.
        
        Store the transport.
        """
        self._transport = transport
    
    def on_data(self, data):
        """
        Called when data is received on the connection.
        """
        
        if self._transport.state == STATE.CONNECTING:
            self._buffer = ''.join([self._buffer, data.decode()])
            if not '\r\n\r\n' in self._buffer:
                raise WSHandshakeError('Client sending data without handshaking')
            
            packet = ''
            
            if self._buffer.find('\r\n\r\n') == len(self._buffer) - 1:
                packet = self._buffer
                self._buffer = ''
            else:
                data = self._buffer.split('\r\n\r\n')
                packet = data[0]
                self._buffer = ''.join(data[1:])
            
            self._handshake(packet)
        else:
            frame = {}
            if self._frame is None:
                frame = {
                    'fin': 0,
                    'opcode': 0,
                    'mask': 0,
                    'hlen': 2,
                    'length': 0,
                    'payload': None,
                    'left': 0,
                    'close_code': 1000,
                    'close_reason': '',
                    'buf': data}
            else:
                frame = self._frame
                frame['buf'] += data
                self._frame = None
            
            blen = frame['buf']
            frame['left'] = blen
            
            if blen < frame['hlen']:
                self._frame = frame
                return
            
            print frame['buf']
            header, payloadlen = STRUCT_BB.unpack(frame['buf'][:2])
            print header, payloadlen
            frame['fin'] = (header >> 7) & 1
            frame['opcode'] = header & 0xf
            masked = (payloadlen >> 7) & 1
            frame['masked'] = masked
            reserved_bits = header & 0x70
            print frame['fin']
            print frame['opcode']
            print frame['masked']
    
    def _handshake(self, packet):
        """
        Process a handshake attempt.
        """
        request = http.Request(packet)
        
        # Has to be a GET
        if request.command is None or request.command != 'GET':
            raise WSHandshakeError('Client sending data without handshaking')
        
        # Needs to be at least HTTP/1.1
        if float(request.request_version.split('/')[-1]) < 1.1:
            raise WSHandshakeError('Incompatible HTTP version')
        
        # Should have headers, and we need an upgrade header.
        if not hasattr(request, 'headers') or 'upgrade' not in request.headers:
            raise WSHandshakeError('No header values given')
        
        # Needs to be requesting a WebSocket connection.
        if 'websocket' not in request.headers['upgrade'].lower():
            raise WSHandshakeError('Invalid Upgrade header')
        
        # Needs to be requesting a connection upgrade.
        if 'connection' not in request.headers or 'upgrade' not in request.headers['connection'].lower():
            raise WSHandshakeError('Invalid Connection header')
        
        # Needs to be using WebSocket protocol version 13.
        if 'sec-websocket-version' not in request.headers or request.headers['sec-websocket-version'] != '13':
            raise WSHandshakeError('Incompatible WebSocket version')
        
        # Needs to provide a key.
        if 'sec-websocket-key' not in request.headers:
            raise WSHandshakeError('No key provided')
        
        # Ok, now we let the on_handshake method take over.
        # If None is returned then we have to sort out the handshake ourself.
        if self.on_handshake(request) is None:
            written = self._transport.accept(request.headers['sec-websocket-key'])
            if written > -1:
                self.on_open()
    
    def on_handshake(self, request):
        """
        Handshake received.
        """
        return None
    
    def on_open(self):
        """
        Connection established and handshake complete.
        """
    




