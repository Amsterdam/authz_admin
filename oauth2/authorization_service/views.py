"""
    oauth2.authorization_service.requesthandlers
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from aiohttp.web import Response

import oauth2.rfc6749
from oauth2 import clientregistry, scoperegistry


@oauth2.rfc6749.authorizationrequest(
    clientregistry=clientregistry.get(), known_scopes=scoperegistry.get())
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
