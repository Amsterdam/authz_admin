"""
    oauth2.authorization_service.requesthandlers
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from . import responses, requests

GRANT_FLOWS = {
    'token': responses.authorization_implicit_grant
}


@requests.authorization(*GRANT_FLOWS.keys())
async def authorization_request(request):
    """
    MUST use TLS.
    MUST support GET, MAY support POST.
    """
    # Step 6: Handle request
    return GRANT_FLOWS[request.response_type](request)
