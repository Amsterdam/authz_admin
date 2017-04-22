"""
    oauth2.rfc6749.exceptions
    ~~~~~~~~~~~~~~~~~~~~~~~~~
"""


class RFC6749Error(Exception):
    """ Base class for all RFC related runtime errors
    """


class UnknownResponseTypeError(RFC6749Error):
    """ The response_type parameter given in the AuthorizationRequest is
    unknown.
    """
