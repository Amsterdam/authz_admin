import uuid

from . import authorizationrequest, authorizationresponse

authz_cache = dict()  # <- placeholder for Redis, memcached, or something else
idp_cache = dict()


class RequestHandler:
    """Async handlers for all endpoints."""

    def __init__(self, idpregistry, clientregistry, scoperegistry):
        # language=rst
        """Constructor.

        :param idpregistry:
        :param clientregistry:
        :param scoperegistry:
        """
        self.idpregistry = idpregistry
        self.clientregistry = clientregistry
        self.scoperegistry = scoperegistry

    async def authorization(self, request):
        # language=rst
        """Authorization endpoint (RFC6749 section 3.1)"""
        authzreqparams = authorizationrequest.params(
            request, self.clientregistry, self.scoperegistry
        )

        # Figure out which IdP plugin to use and grab the authentication_redirect
        client = self.clientregistry[authzreqparams.client_id]
        idp_id = request.query.get('idp')
        if not idp_id and len(client.idps) == 1:
            idp_id = client.idps[0]
        if not idp_id:
            return authorizationresponse.InvalidRequest(
                authzreqparams.redirect_uri,
                authzreqparams.state
            )
        if idp_id not in self.idpregistry:
            return authorizationresponse.InvalidRequest(
                authzreqparams.redirect_uri,
                authzreqparams.state
            )
        authentication_redirect, _ = self.idpregistry[idp_id]

        # create a UUID and the callback URI
        request_uuid = uuid.uuid4().hex

        # grab the response from the IdP plugin
        response, *keyvalue = authentication_redirect(request_uuid)
        key, value = keyvalue[0], (len(keyvalue) == 2 and keyvalue[1]) or request_uuid
        idp_cache[key] = value
        return response

    async def idp_callback(self, request):
        # language=rst
        """ IdP callback endpoint
        """
        idp_identifier = request.match_info['idp']
#         if authzreqparams.response_type == 'code':
#             authorization_code = types.AuthorizationCode()
#             if authorization_code in authz_cache:  # <- probability of 2^(-160)
#                 return authorizationresponse.ServerError(
#                     authzreqparams.redirect_uri,
#                     authzreqparams.state
#                 )
#             authz_cache[authorization_code] = authzreqparams
#             return authorizationresponse.AuthorizationCode(
#                 authorization_code,
#                 authzreqparams.redirect_uri,
#                 authzreqparams.state
#             )
#         elif authzreqparams.response_type == 'token':
#             ...  # return accesstoken
