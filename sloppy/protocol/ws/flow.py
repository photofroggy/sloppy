''' sloppy.protocol.wsc.flow - photofroggy
    WebSocket flow control.
'''
import array
import struct
from sloppy.flow import Protocol
from sloppy.flow import ServerFactory
from sloppy.flow import ConnectionFactory
from sloppy.protocol import http
from sloppy.protocol.ws import STATE
from sloppy.protocol.ws.error import WSHandshakeError
from sloppy.protocol.ws.error import WSMessageError
from sloppy.protocol.ws.error import WSFrameError


# Array methods.
try:
    make_array = bytearray
    to_string = bytes_type
except NameError:
    make_array = lambda d: array.array("B", d)
    to_string = lambda d: d.tostring()


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
        return self._protocol()
    
    def fail(self, transport, reason=None):
        """
        Connection attempt failed.
        """
        raise reason
    
    def closed(self, transport, reason=None):
        """
        A connection was closed.
        """
        #print transport.conn.getpeername()


class WebSocketProtocol(Protocol):
    """
    Implements base functionality for the WebSocket protocols.
    """
    
    def log(self, *msg):
        """
        Display a log message.
        """
        if self._transport is None:
            return
        self._transport.log(*msg)
    
    def _message(self, opcode, data):
        """
        Handle a WebSocket message.
        """
        if opcode not in [0x1, 0x2, 0x8, 0x9, 0xA]:
            raise WSMessageError('Unknown opcode {0}'.format(opcode))
        else:
            self.log('received message')
        
        if opcode == 0x1:
            # UTF-8
            try:
                data = data.decode('utf8')
            except UnicodeDecodeError as e:
                raise WSMessageError('Couldn\'t decode; {0}'.format(e.message))
            self.on_message(data)
            return
        
        if opcode == 0x2:
            # Binary
            self.on_binary(data)
            return
        
        if opcode == 0x8:
            # Close
            self.on_close()
            self._transport.close()
            return
        
        if opcode == 0x9:
            # Ping
            self.on_ping()
            WSMessageError('Ping not implemented')
            return
        
        if opcode == 0xA:
            # Pong
            self.on_pong()
            WSMessageError('Pong not implemented')
            return
        
    
    def on_handshake(self, request):
        """
        Handshake received.
        
        If writing the response from here, return True.
        Otherwise, return None or don't return anything.
        """
        return None
    
    def on_open(self):
        """
        Connection established and handshake complete.
        """
    
    def on_message(self, message):
        """
        Message received.
        """
    
    def on_binary(self, message):
        """
        Binary message received.
        """
    
    def on_close(self, message):
        """
        Close frame received.
        """
    
    def on_ping(self, message):
        """
        Ping frame received.
        """
    
    def on_pong(self, message):
        """
        Pong frame received.
        """


class WebSocketServerProtocol(WebSocketProtocol):
    """
    Base protocol object for WebSocket server connections.
    """
    
    def __init__(self):
        self._transport = None
        self._buffer = ''
        self._frame = None
        #self._factory = factory
    
    def connected(self, transport):
        """
        A new client has connected to the server.
        
        Store the transport.
        """
        self._transport = transport
        
        if 'server' in transport.__class__.__name__.lower():
            self.log('listening on port {0}'.format(transport.port))
            return
        
        self.log('socket accepted')
    
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
            
            self.log('handshake received')
            self._handshake(packet)
        else:
            frame = {}
            if self._frame is None:
                frame = {
                    'fin': 0,
                    'opcode': 0,
                    'rop': 0,
                    'control': 0,
                    'mask': 0,
                    'hlen': 2,
                    'length': 0,
                    'payload': None,
                    'left': 0,
                    'close_code': 1000,
                    'close_reason': '',
                    'fbuf': None,
                    'buf': data}
            else:
                frame = self._frame
                frame['buf'] = data
            
            blen = frame['buf']
            frame['left'] = blen
            
            if blen < frame['hlen']:
                self._frame = frame
                return
            
            header, payloadlen = STRUCT_BB.unpack(frame['buf'][:2])
            frame['buf'] = frame['buf'][2:]
            
            if header & 0x70:
                raise WSFrameError('Header using undefined bits', frame)
            
            frame['fin'] = header & 0x80
            frame['opcode'] = header & 0xf
            frame['control'] = frame['opcode'] & 0x8
            frame['masked'] = payloadlen & 0x80
            frame['length'] = payloadlen & 0x7f
            
            if not frame['masked']:
                raise WSFrameError('Unmasked frame', frame)
            
            if frame['control'] and frame['length'] >= 126:
                raise WSFrameError('Control payload too big', frame)
            
            if self._frame is None:
                frame['rop'] = header & 0xf
            else:
                self._frame = None
            
            if frame['length'] < 126:
                self._unmask(frame)
            elif frame['length'] == 126:
                self._frame16(frame)
            elif frame['length'] == 127:
                self._frame64(frame)
    
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
        if not self.on_handshake(request):
            written = self._transport.accept(request.headers['sec-websocket-key'])
            
            if written > -1:
                self.on_open()
            
            return
        
        self.on_open()
    
    def _unmask(self, frame):
        """
        Unmask a WebSocket frame.
        """
        frame['mask'] = make_array(frame['buf'][:4])
        frame['buf'] = frame['buf'][4:]
        data = make_array(frame['buf'][:frame['length']])
        
        for i in xrange(len(frame['buf'])):
            data[i] = data[i] ^ frame['mask'][i % 4]
        
        frame['buf'] = frame['buf'][frame['length']:]
        self._frame_data(frame, data)
    
    def _frame16(self, frame):
        """
        Parse a 16bit WebSocket frame.
        """
        frame['length'] = STRUCT_H.unpack(frame['buf'][:2])[0]
        frame['buf'] = frame['buf'][2:]
        self._unmask(frame)
    
    def _frame64(self, frame):
        """
        Parse a 64bit WebSocket frame.
        """
        frame['length'] = STRUCT_Q.unpack(frame['buf'][:8])[0]
        frame['buf'] = frame['buf'][8:]
        self._unmask(frame)
    
    def _frame_data(self, frame, data):
        """
        Parse WebSocket frame data.
        """
        op = frame['opcode']
        
        if frame['control']:
            if not frame['fin']:
                raise WSFrameError('Fragmented control frame received')
            op = frame['rop']
        elif frame['opcode'] == 0:
            if frame['fbuf'] is None:
                raise WSFrameError('Received continuation frame with empty buffer')
            
            frame['fbuf'] += data
            
            if frame['fin']:
                data = frame['fbuf']
        else:
            if frame['fbuf'] is not None:
                raise WSFrameError('Received new message while buffer was not empty')
            
            if not frame['fin']:
                frame['fbuf'] = data
        
        if frame['fin']:
            self._message(op, to_string(data))
            return
        
        self._frame = frame
    




