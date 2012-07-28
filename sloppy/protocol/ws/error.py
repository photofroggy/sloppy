''' sloppy.protocol.ws.error - photofroggy
    Exceptions for the WebSocket stuff.
'''
from sloppy.error import ConnectionError


class WSHandshakeError(ConnectionError):
    """
    An error happened when trying to handshake.
    """



