''' sloppy.protocol.transport - photofroggy
    WebSocket transports.
'''
import base64
import hashlib
from sloppy.transport import TCPServer
from sloppy.transport import TCPClient
from sloppy.protocol.ws.flow import WebSocketServerFactory


class STATE:
    """
    Basically an enum determining the state of a connection.
    """
    
    CONNECTING = 0
    OPEN = 1
    TIME_WAIT = 2
    CLOSING = 3
    CLOSED = 4


SERVER_HANDSHAKE = 'HTTP/1.1 101 WebSocket Accept\r\n{0}\r\n\0'

CLIENT_HANDSHAKE = 'GET {0} HTTP/1.1\r\n'

PADDING = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'


class WebSocketServer(TCPServer):
    """
    Transport for WebSocket servers.
    
    This transport listens for new socket connections on a given address
    and port. New connections are accepted and wrapped with a WebSocketClient
    Transport object by default.
    
    By default, the WebSocketServerFactory is used for spawning new client
    transports, and manages protocol that is used to do this.
    """
    
    def __init__(self, addr, port, factory=None, transport=None, protocol=None, *args, **kwargs):
        """
        Create a transport.
        """
        self.addr = addr
        self.port = port
        self.factory = factory or WebSocketServerFactory(protocol)
        self._transport = transport or WebSocketClient
        self.init(addr, port, factory, transport, *args, **kwargs)
    
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


class WebSocketClient(TCPClient):
    """
    Transport for WebSocket clients.
    
    This transport wraps a socket connection to a remote host. Messages sent
    are wrapped appropriately according to the WebSocket standard 
    """
    
    def __init__(self, addr, port, factory=None, *args, **kwargs):
        """
        Create a transport.
        """
        self.addr = addr
        self.port = port
        self.state = STATE.CONNECTING
        self.factory = factory or ConnectionFactory()
        self.dcreason = None
        self.init(addr, port, factory, *args, **kwargs)
    
    def accept(self, key, protocol=None, extensions=None, extra=None *args, **kwargs):
        """
        Accept a WebSocket connection.
        
        Here, we send a server handshake packet and set the connection's state
        to OPEN.
        """
        self.state = STATE.OPEN
        enc = hashlib.sha1()
        enc.update(key)
        enc.update(PADDING)
        key = base64.b64encode(enc.digest())
        headers = [
            'Upgrade: WebSocket\r\n',
            'Connection: Upgrade\r\n',
            'Sec-WebSocket-Accept: {0}\r\n'.format(key)]
        
        if protocol is not None:
            headers.append('Sec-WebSocket-Protocol: {0}\r\n'.format(protocol))
        
        if extensions is not None:
            headers.append('Sec-WebSocket-Extension: {0}\r\n'.format(extensions))
        
        if extra is not None:
            headers.extend(extra)
        
        written = self.write(SERVER_HANDSHAKE.format(''.join(headers)).encode())
        
        if written > -1:
            self.state = STATE.OPEN
            return written
        
        self.state = STATE.CLOSED
        return written


