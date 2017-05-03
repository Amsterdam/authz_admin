"""
    oauth2.authorization_service.requesthandlers
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from aiohttp.web import Response

import oauth2.rfc6749
import oauth2.clientregistry
import oauth2.scoperegistry

clientregistry = oauth2.clientregistry.get()
scoperegistry = oauth2.scoperegistry.get()


@oauth2.rfc6749.authorizationrequest(clientregistry, scoperegistry)
async def authorizationrequest(request):
    """ OAuth 2.0 Authorization Request

    MUST use TLS.
    MUST support GET, MAY support POST.
    """
    scope = request.scope
    state = request.state
    client_id = request.client_id
    redirect_uri = request.redirect_uri
    return Response(body='{} {} {} {}'.format(
        scope, state, client_id, redirect_uri
    ))

async def confirm_authorization(request):
    """ Post-authentication callback resource
    """
