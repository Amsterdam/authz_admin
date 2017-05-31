"""
    oauth2.idp.tma_oauth2
    ~~~~~~~~~~~~~~~~~~~~~

    TMA OAuth 2.0 IdP plugin. Requires these entries in its config:

    - client_id: The client identifier
    - authorization_uri: The OAuth 2.0 authorization endpoint
"""
import secrets
import urllib.parse

from aiohttp import web


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
    if not {'client_id', 'authorization_uri', 'callback_uri'} <= config.keys():
        raise Exception('To use the TMA Oauth 2.0-based IdP you must provide'
                        ' client_id, authorization_uri and callback_uri')

    queryparams = {'client_id': config['client_id']}
    separator = (config['authorization_uri'].find('?') < 0 and '?') or '&'
    authn_redirect_base = config['authorization_uri'] + separator

    def authentication_redirect(_):
        """ Create the authentication redirect and identifier.

        :param _: ignore the given uuid; we don't return a ``value`` so the
            uuid will be stored.
        """
        state = secrets.token_urlsafe(nbytes=20)
        queryparams['state'] = state
        queryparams['redirect_uri'] = config['callback_uri']
        response = web.HTTPSeeOther(
            authn_redirect_base + urllib.parse.urlencode(queryparams)
        )
        return response, state

    def validate_authentication(request, get_and_delete):
        ...

    return authentication_redirect, validate_authentication
