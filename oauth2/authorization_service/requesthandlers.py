"""
    oauth2.requesthandlers
    ~~~~~~~~~~~~~~~~~~~~~~
"""
from aiohttp import web, web_exceptions

from oauth2 import clientregistry

GRANT_CODE = 'code'
GRANT_IMPLICIT = 'token'


async def authorization_request(request):
    """
    MUST use TLS.
    MUST support GET, MAY support POST.
    Request arguments sent without a value MUST be treated as if they were
    omitted from the request.
    The authorization server MUST ignore unrecognized request parameters.
    Request and response parameters MUST NOT be included more than once.

    Request query string (application/x-www-form-urlencoded) arguments:

    response_type
        REQUIRED.  Value MUST be set to "token" for an implicit grant, or to
        "code" for an authorization code grant.

    client_id
        REQUIRED.  The client identifier as described in Section 2.2.

    redirect_uri
        OPTIONAL if only one redirect endpoint was registered for this client,
        REQUIRED if more

    scope
        OPTIONAL.  The scope of the access request as described by Section 3.3.

    state
        REQUIRED (RECOMMENDED by RFC).  An opaque value used by the client to
        maintain state between the request and callback.  The authorization
        server includes this value when redirecting the user-agent back to the
        client.  The parameter SHOULD be used for preventing cross-site request
        forgery as described in Section 10.12.


    Error handling:

        If the request fails due to a missing, invalid, or mismatching
        redirection URI, or if the client identifier is missing or invalid, the
        authorization server SHOULD inform the resource owner of the error and
        MUST NOT automatically redirect the user-agent to the invalid
        redirection URI.
    """
    # Step 1: Make sure the client identifier is present and valid
    # TODO: once the client identifier format has been decided on we could do
    #       more validity checks before querying the clientregistry.
    client_id = request.query.get('client_id')
    client = client_id and clientregistry.get(client_id)
    if not client:
        raise web_exceptions.HTTPBadRequest(
            reason='invalid client_id'
        )
    # Step 2: Make sure we redirect the user to a valid redirect_uri
    redirect_uri = request.query.get('redirect_uri')
    if redirect_uri:
        redirect_uri = redirect_uri in client.redirect_uris and redirect_uri
    else:
        redirect_uri = len(client.redirect_uris) == 1 and client.redirect_uris[0]
    if not redirect_uri:
        raise web_exceptions.HTTPBadRequest(
            reason='invalid redirect_uri'
        )

    state = request.query.get('state')
    if not state:
        ...
    response_type = request.query.get('response_type')
    if response_type not in (GRANT_CODE, GRANT_IMPLICIT):
        ...
