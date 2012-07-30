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


class WSError(ConnectionError):
    """
    Base class for all WebSocket errors.
    """


class WSHandshakeError(WSError):
    """
    An error happened when trying to handshake.
    """


class WSFrameError(WSError):
    """
    Received a mal-formed WebSocket frame.
    """


