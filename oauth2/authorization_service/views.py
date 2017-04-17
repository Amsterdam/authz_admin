"""
    oauth2.authorization_service.requesthandlers
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from . import responses
from .decorators import authorizationrequest

GRANT_FLOWS = {
    'token': responses.authorization_implicit_grant
}


@authorizationrequest(*GRANT_FLOWS.keys())
async def authorizationrequest(request):
    """
    MUST use TLS.
    MUST support GET, MAY support POST.
    """
    return GRANT_FLOWS[request.response_type](request)
