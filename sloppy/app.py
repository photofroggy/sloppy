''' sloppy.app - photofroggy
    Main application loop code in here bitches.
'''

import socket
import select
import errno
from sloppy.error import ConnectionError
from sloppy.transport import Transport


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
    
    def connect(self, transport):
        """
        Connect to a server.
        """
        if self.running:
            self.open(transport)
            return
        
        self.cqueue.append([transport])
    
    def open(self, transport):
        """
        Open a connection on a transport.
        """
        if not transport.connect():
            return
        
        protocol = transport.protocol()
        self.conn.append([ transport, protocol ])
        self.cobj.append(transport.conn)
        protocol.connected(transport)
    
    def accept(self, transport):
        """
        Accept and serve a socket connection.
        """
        protocol = transport.protocol()
        self.conn.append([ transport, protocol ])
        self.cobj.append(transport.conn)
        protocol.connected( transport )
    
    def start_connections(self):
        """
        Start any connections in the queue.
        """
        while len(self.cqueue) > 0:
            conn = self.cqueue.pop(0)
            self.open(conn[0])
    
    def clean_connections(self):
        """
        Get rid of any closed sockets.
        """
        ncobj = []
        nconn = []
        
        for i, cobj in enumerate(self.cobj):
            conn = self.conn[i]
            
            if conn[0].conn is None:
                dcr = conn[0].dcreason
                conn[1].connection_closed(dcr)
                conn[0].closed(dcr)
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
                    try:
                        conn[1].data_received(data)
                        continue
                    except ConnectionError as err:
                        # An error happened, causing us to disconnect.
                        data = err
                
                if isinstance(data, Transport):
                    # Something connected. Accept the connection.
                    self.accept(data)
                    continue
                
                # If we get here then the connection has been closed.
                # Call related methods on objects and remove the connection from
                # our pool.
                conn[0].close()
                conn[1].connection_closed( data )
                self.cobj.pop(index)
                self.conn.pop(index)
                conn[0].closed(data)
            
            self.clean_connections()
        
        # Cleanup!
    
    def stop(self):
        """
        Stop the application.
        """
        self.running = False
