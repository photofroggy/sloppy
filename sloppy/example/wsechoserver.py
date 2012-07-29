import sloppy
from sloppy.protocol.ws.flow import WebSocketServerProtocol
from sloppy.protocol.ws.transport import WebSocketServer


class EchoProtocol(WebSocketServerProtocol):
    """
    All we want to do is send anything that comes through the socket back to
    the client.
    """
    
    def on_open(self):
        """
        WebSocket connection opened.
        """
        print '>> connection open'
    
    def on_message(self, data):
        print ">> Received:", data.decode()
        #self.conn.write((data.decode() + " foo").encode())


class MyApplication(sloppy.Application):
    
    def init(self, addr, port):
        self.connect(WebSocketServer(addr, port, protocol=EchoProtocol))
        print ">> Serving", addr, "on port", port

if __name__ == '__main__':
    app = MyApplication( '0.0.0.0', 8000 )
    app.start()

