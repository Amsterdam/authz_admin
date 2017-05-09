"""
    oauth2.authorization_service.requesthandlers
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from . import authorizationrequest, authorizationresponse
from oauth2 import types

cache = dict()  # <- placeholder for Redis, memcached, or something else


class RequestHandler:
    """ Async handlers for all endpoints.
    """

    def __init__(self, idpregistry, clientregistry, scoperegistry):
        """ Constructor.

        :param idp:
        :param clientregistry:
        :param scoperegistry:
        """
        self.idpregistry = idpregistry
        self.clientregistry = clientregistry
        self.scoperegistry = scoperegistry

    async def authorization(self, request):
        """ Authorization endpoint (RFC6749 section 3.1)
        """
        authzreqparams = authorizationrequest.params(
            request, self.clientregistry, self.scoperegistry
        )

        untrusted_client = self.clientregistry[authzreqparams.client_id].secret is None
        if untrusted_client and authzreqparams.response_type != 'code':
            return authorizationresponse.UnauthorizedClient(
                authzreqparams.redirect_uri,
                authzreqparams.state
            )

        authorization_code = types.AuthorizationCode()
        if authorization_code in cache:  # <- probability of 2^(-160)
            return authorizationresponse.ServerError(
                authzreqparams.redirect_uri,
                authzreqparams.state
            )

        cache[authorization_code] = authzreqparams

        if authzreqparams.response_type == 'code':
            return authorizationresponse.AuthorizationCode(
                authorization_code,
                authzreqparams.redirect_uri,
                authzreqparams.state
            )
        elif authzreqparams.response_type == 'token':
            ...  # return accesstoken

    async def idp_code(self, request):
        """ Authorization code IdP callback endpoint
        """
        idp_identifier = request.match_info['idp']

    async def idp_token(self, request):
        """ Access token IdP callback endpoint
        """
        idp_identifier = request.match_info['idp']
