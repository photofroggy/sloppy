import sloppy


class Client(sloppy.ConnectionFactory):
    
    def __init__(self, app):
        self.app = app
    
    def protocol(self):
        return EchoProto(self)
    
    def fail(self, transport, reason):
        self.app.stop()
    
    def closed(self, transport, reason):
        self.app.stop()
    

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
        self.connect(sloppy.TCPClient( 'localhost', 8000, Client(self)))

if __name__ == '__main__':
    app = MyApplication()
    app.start()
