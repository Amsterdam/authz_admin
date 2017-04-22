"""
    oauth2.authorization_service.requesthandlers
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from oauth2.rfc6749 import authorizationrequest
from oauth2 import clientregistry


@authorizationrequest(clientregistry=clientregistry)
async def authorizationrequest(request):
    """
    MUST use TLS.
    MUST support GET, MAY support POST.
    """
    return ''
