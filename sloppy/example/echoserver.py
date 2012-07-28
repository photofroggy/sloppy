import sloppy
    

class Protocol(sloppy.Protocol):
    """
    All we want to do is send anything that comes through the socket back to
    the client.
    """
    
    def connected(self, transport):
        self.conn = transport
    
    def on_data(self, data):
        print ">> Received:", data.decode()
        self.conn.write((data.decode() + " foo").encode())


class MyApplication(sloppy.Application):
    
    def init(self, addr, port):
        self.connect(sloppy.TCPServer(addr, port, protocol=Protocol))
        print ">> Serving", addr, "on port", port

if __name__ == '__main__':
    app = MyApplication( '127.0.0.1', 8000 )
    app.start()

