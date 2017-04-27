"""
    oauth2.authorization_service.requesthandlers
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import oauth2.rfc6749
from oauth2 import clientregistry, scoperegistry


@oauth2.rfc6749.authorizationrequest(
    clientregistry=clientregistry.get(), known_scopes=scoperegistry.get())
async def authorizationrequest(request):
    """
    MUST use TLS.
    MUST support GET, MAY support POST.
    """
    return ''
