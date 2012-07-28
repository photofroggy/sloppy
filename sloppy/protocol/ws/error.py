''' sloppy.protocol.ws.error - photofroggy
    Exceptions for the WebSocket stuff.
'''
from sloppy.error import ConnectionError


class ERROR:
    """
    Enum for error types.
    """
    
    CONNECTION = 0
    HANDSHAKE = 1


class WSHandshakeError(ConnectionError):
    """
    An error happened when trying to handshake.
    """



