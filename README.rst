--------
sloppy
--------

**sloppy** is simple, pure python package, which aids in networking using
Python's sockets. The API is loosely based on twisted.

=========================
Why not just use twisted?
=========================

Twisted is a bit of a huge unrequired mammoth for small projects that only need
very basic socket handling.

=============
Echo example
=============

As an example, here is a simple echo server and client. First, the client::

    import sloppy
    
    class Client(sloppy.ConnectionFactory):
        
        def __init__(self, app):
            self.app = app
        
        def protocol(self):
            return EchoProto(self)
        
        def fail(self, transport, reason):
            self.app.stopLoop()
        
        def closed(self, transport, reason):
            self.app.stopLoop()
        

    class EchoProto(sloppy.Protocol):
        
        def __init__(self, client):
            self.client = client
        
        def connected(self, transport):
            self.c = transport
            print ">> hello world"
            self.c.write('hello world'.encode())
        
        def data_received(self, data):
            print "<< " + (data.decode()).strip()
            self.c.close()


    class MyApplication(sloppy.Application):
        
        def init(self):
            self.connect(
                sloppy.TCPClient( 'localhost', 8000 ),
                Client(self)
            )

    if __name__ == '__main__':
        app = MyApplication()
        app.start()

And the server::

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
            self.connect(
                sloppy.TCPServer( addr, port ),
                EchoServ()
            )
            print ">> Serving", addr, "on port", port

    if __name__ == '__main__':
        app = MyApplication( '127.0.0.1', 8000 )
        app.start()

