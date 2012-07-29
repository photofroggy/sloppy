''' sloppy.ws - photofroggy
    Implements the WebSocket protocol.
'''


class STATE:
    """
    Basically an enum determining the state of a connection.
    """
    
    CONNECTING = 0
    OPEN = 1
    TIME_WAIT = 2
    CLOSING = 3
    CLOSED = 4

