''' sloppy.app - photofroggy
    Main application loop code in here bitches.
'''

import socket
import select
import errno


class Application(object):
    """
    Use this object for the application loop.
    """
    
    running = False
    cqueue = [] # [ [ address, port, factory ] ]
    conn = []
    
    def __init__(self, *args, **kwargs):
        self.running = False
        self.cqueue = []
        self.conn = []
        self.cobj = []
        self.init(*args, **kwargs)
    
    def init(self, *args, **kwargs):
        """
        Main application method.
        """
    
    def connect(self, transport, factory):
        """
        Connect to a server.
        """
        if self.running:
            self.open(transport, factory)
            return
        
        self.cqueue.append([transport, factory])
    
    def open(self, sock, factory):
        """
        Open a connection on a transport.
        """
        factory.starting()
        err = sock.connect()
        
        if err is not None:
            factory.fail(sock, err)
            return
        
        factory.connected(sock)
        protocol = factory.protocol()
        self.conn.append([ sock, factory, protocol ])
        self.cobj.append(sock.conn)
        protocol.connected(sock)
    
    def accept(self, transport, factory):
        """
        Accept and serve a socket connection.
        """
        protocol = factory.protocol()
        self.conn.append([ transport, None, protocol ])
        self.cobj.append(transport.conn)
        protocol.connected( transport )
    
    def start_connections(self):
        """
        Start any connections in the queue.
        """
        while len(self.cqueue) > 0:
            conn = self.cqueue.pop(0)
            self.open(conn[0], conn[1])
    
    def clean_connections(self):
        """
        Get rid of any closed sockets.
        """
        ncobj = []
        nconn = []
        
        for i, cobj in enumerate(self.cobj):
            conn = self.conn[i]
            
            if conn[0].conn is None:
                conn[2].connection_closed( None )
                
                if conn[1] is not None:
                    conn[1].closed( conn[0], None )
                
                continue
            
            nconn.append( conn )
            ncobj.append( cobj )
        
        self.cobj = ncobj
        self.conn = nconn
    
    def start(self):
        """
        Start the application.
        """
        self.start_connections()
        self.clean_connections()
        self.main_loop()
    
    def main_loop(self):
        """
        Main application loop.
        """
        self.running = True
        
        while self.running:
            read, write, err = select.select(self.cobj, [], self.cobj, .5)
            
            for s in read:
                index = self.cobj.index( s )
                conn = self.conn[index]
                data = conn[0].read(8192)
                
                if data is None:
                    # Nothing to do at the moment. Ignore everything I guess.
                    continue
                
                if isinstance(data, str):
                    # Received some raw data on a connection.
                    conn[2].data_received(data)
                    continue
                
                if isinstance(data, Transport):
                    # Something connected. Accept the connection.
                    self.accept(data, conn[1])
                    continue
                
                # If we get here then the connection has been closed.
                # Call related methods on objects and remove the connection from
                # our pool.
                conn[0].close()
                conn[2].connection_closed( data )
                
                if conn[1] is not None:
                    conn[1].closed( conn[0], data )
                
                self.cobj.pop(index)
                self.conn.pop(index)
            
            self.clean_connections()
        
        # Cleanup!
    
    def stop(self):
        """
        Stop the application.
        """
        self.running = False
