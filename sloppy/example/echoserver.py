import sloppy


class EchoServ(sloppy.ConnectionFactory):
    """
    All we need for a factory here is something that creates an appropriate
    protocol for each connection.
    """
    
    def protocol(self):
        return EchoProto()
    

class EchoProto(sloppy.Protocol):
    """
    All we want to do is send anything that comes through the socket back to
    the client.
    """
    
    def connected(self, transport):
        self.conn = transport
    
    def data_received(self, data):
        print ">> Received:", data.decode()
        self.conn.write((data.decode() + " foo").encode())


class MyApplication(sloppy.Application):
    
    def init(self, addr, port):
        self.connect(sloppy.TCPServer( addr, port, EchoServ()))
        print ">> Serving", addr, "on port", port

if __name__ == '__main__':
    app = MyApplication( '127.0.0.1', 8000 )
    app.start()

