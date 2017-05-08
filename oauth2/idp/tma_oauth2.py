"""
    oauth2.idp.tma_oauth2
    ~~~~~~~~~~~~~~~~~~~~~

    TMA OAuth 2.0 IdP plugin. Requires these entries in its config:

    - client_id: The client identifier
    - authorization_uri: The OAuth 2.0 authorization endpoint
"""

IDP_ID = 'tma_oauth2'
""" Identifier of the TMA Oauth 2.0 interface
"""


def get(config):
    """ Closure that returns the implementation of our IdP interface, bound to
    the given configuration.

    :param config:
        The configuration dictionary

    :raise Exception:
        If the given configuration is invalid

    :return tuple:
        Two callables confirming to our contract: authentication_redirect(uuid)
        and validate_authentication(request, get_and_delete)
    """
    if not {'client_id', 'authorization_uri'} <= config.keys():
        raise Exception('To use the TMA Oauth 2.0-based IdP you must provide'
                        ' a client_id and authorization_uri')

    def authentication_redirect(uuid):
        ...

    def validate_authentication(request, get_and_delete):
        ...

    return authentication_redirect, validate_authentication
