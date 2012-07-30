import sys
import sloppy
from sloppy.protocol.ws.flow import WebSocketServerProtocol
from sloppy.protocol.ws.transport import WebSocketServer


class EchoProtocol(WebSocketServerProtocol):
    """
    All we want to do is send anything that comes through the socket back to
    the client.
    """
    
    '''
    def on_handshake(self, request):
        print request.headers['sec-websocket-extensions']'''
    
    def on_open(self):
        """
        WebSocket connection opened.
        """
        self.log('websocket open')
    
    def on_message(self, data):
        self.log('Received:', data)
        #self.conn.write((data.decode() + " foo").encode())


if __name__ == '__main__':
    app = sloppy.Application()
    app.connect(WebSocketServer('0.0.0.0', 8000, protocol=EchoProtocol))
    app.start()

