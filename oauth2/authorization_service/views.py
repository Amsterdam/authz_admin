"""
    oauth2.authorization_service.requesthandlers
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import oauth2.rfc6749.authorizationresponse
import oauth2.rfc6749.authorizationrequest
import oauth2.rfc6749.types
import oauth2.clientregistry
import oauth2.scoperegistry

clientregistry = oauth2.clientregistry.get()
scoperegistry = oauth2.scoperegistry.get()

cache = dict()  # <- placeholder for Redis, memcached, or something else


async def authorizationrequest(request):
    """ OAuth 2.0 Authorization Request
    """
    authorizationrequestparams = oauth2.rfc6749.authorizationrequest.parse(
        request, clientregistry, scoperegistry
    )

    authorization_code = oauth2.rfc6749.types.AuthorizationCode()
    if authorization_code in cache:  # <- probability of 2^(-160)
        return oauth2.rfc6749.authorizationresponse.ServerError(
            authorizationrequestparams.redirect_uri,
            authorizationrequestparams.state
        )

    cache[authorization_code] = authorizationrequestparams

    return oauth2.rfc6749.authorizationresponse.Success(
        authorization_code,
        authorizationrequestparams.redirect_uri,
        authorizationrequestparams.state
    )

async def accesstoken(request):
    """ Accesstoken endpoint
    """
