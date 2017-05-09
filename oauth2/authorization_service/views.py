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
    """ Authorization endpoint (RFC6749 section 3.1)
    """
    authorizationrequestparams = oauth2.rfc6749.authorizationrequest.params(
        request, clientregistry, scoperegistry
    )

    authorization_code = oauth2.rfc6749.types.AuthorizationCode()
    if authorization_code in cache:  # <- probability of 2^(-160)
        return oauth2.rfc6749.authorizationresponse.ServerError(
            authorizationrequestparams.redirect_uri,
            authorizationrequestparams.state
        )

    cache[authorization_code] = authorizationrequestparams

    if authorizationrequestparams.response_type == 'code':
        return oauth2.rfc6749.authorizationresponse.AuthorizationCode(
            authorization_code,
            authorizationrequestparams.redirect_uri,
            authorizationrequestparams.state
        )
    elif authorizationrequestparams.response_type == 'token':
        ...  # return accesstoken


async def idp_code(request):
    """ Authorization code IdP callback endpoint
    """
    idp_identifier = request.match_info['idp']


async def idp_token(request):
    """ Access token IdP callback endpoint
    """
    idp_identifier = request.match_info['idp']
