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
        sys.stdout.write('>> connection open\n')
        sys.stdout.flush()
    
    def on_message(self, data):
        sys.stdout.write('>> Received:' + data.decode() + '\n')
        sys.stdout.flush()
        #self.conn.write((data.decode() + " foo").encode())


class MyApplication(sloppy.Application):
    
    def init(self, addr, port):
        self.connect(WebSocketServer(addr, port, protocol=EchoProtocol))

if __name__ == '__main__':
    app = MyApplication( '0.0.0.0', 8000 )
    app.start()

