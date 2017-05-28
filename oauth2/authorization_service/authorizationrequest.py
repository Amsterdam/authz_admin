"""
This module implements the OAuth2 authorization request as defined in
:rfc:`6749#section-4.1.1` and :rfc:`6749#section-4.2.1`:

.. code-block:: text

    The client constructs the request URI by adding the following
    parameters to the query component of the authorization endpoint URI
    using the "application/x-www-form-urlencoded" format, per Appendix B:

    response_type
        REQUIRED.  Value MUST be set to "code".

    client_id
        REQUIRED.  The client identifier as described in Section 2.2.

    redirect_uri
        OPTIONAL.  As described in Section 3.1.2.

    scope
        OPTIONAL.  The scope of the access request as described by
        Section 3.3.

    state
        RECOMMENDED.  An opaque value used by the client to maintain
        state between the request and callback.  The authorization
        server includes this value when redirecting the user-agent back
        to the client.  The parameter SHOULD be used for preventing
        cross-site request forgery as described in Section 10.12.

Usage::

    authorizationrequestparams = oauth2.rfc6749.authorizationrequest.parse(
        request, clientregistry, scoperegistry
    )

"""
import collections

from aiohttp import web_exceptions

from . import authorizationresponse
from oauth2 import types, decorators

SUPPORTED_RESPONSE_TYPES = frozenset({'code', 'token'})

AuthorizationRequestParams = collections.namedtuple(
    'AuthorizationRequestParams',
    'client_id redirect_uri response_type state scope'
)


def params(request, clientregistry, scoperegistry):
    paramparser = ParamParser(request, clientregistry, scoperegistry)
    return AuthorizationRequestParams(
        client_id=paramparser.client_id,
        redirect_uri=paramparser.redirect_uri,
        state=paramparser.state,
        scope=paramparser.scope,
        response_type=paramparser.response_type
    )


class ParamParser:
    """
    Provides request parsing for an authorization request.

    Notes from :rfc:`6749#section-3.1`:

    *   Parameters sent without a value MUST be treated as if they were omitted
        from the request.
    *   The authorization server MUST ignore unrecognized request parameters.
    *   Request and response parameters MUST NOT be included more than once.

    .. todo::

        How can we check whether a request parameter was included more than
        once? (point 3 above)

    """

    def __init__(self, request, clientregistry, scoperegistry):
        self.request = request
        self.clientregistry = clientregistry
        self.scoperegistry = scoperegistry

    @decorators.reify
    def client_id(self):
        """ The client_id included in the request. (REQUIRED)

        :raises :ref:`aiohttp.web_exceptions.HTTPBadRequest <aiohttp-web-exceptions>`:
            if the client_id query parameter is not present or invalid

        :todo
            Once we have settled on a format for the client identifier we can
            do more extensive checks.
        """
        client_id = self.request.query.get('client_id', '').encode('ascii')
        if not client_id:
            raise web_exceptions.HTTPBadRequest(body='missing client_id')
        if client_id not in self.clientregistry:
            raise web_exceptions.HTTPBadRequest(body='unknown client id')
        return client_id

    @decorators.reify
    def redirect_uri(self):
        """ The redirect_uri for this request. (OPTIONAL)

        :raises :ref:`aiohttp.web_exceptions.HTTPBadRequest <aiohttp-web-exceptions>`:
            if the redirect_uri parameter is not present, invalid, or mismatching.
        """
        client_redirects = self.clientregistry[self.client_id].redirect_uris
        redirect_uri = self.request.query.get('redirect_uri')
        # The below condition is valid but pretty tricky... treat with care
        if not redirect_uri and len(client_redirects) == 1:
            redirect_uri = client_redirects[0]
        elif redirect_uri not in client_redirects:
            raise web_exceptions.HTTPBadRequest(
                body='must provide valid redirect_uri'
            )
        return redirect_uri

    @decorators.reify
    def state(self):
        """ The state parameter for this request. (RECOMMENDED)
        """
        return self.request.query.get('state')

    @decorators.reify
    def response_type(self):
        """ The response_type for this request. (REQUIRED)

        :raises authorizationresponse.InvalidRequest:
            If the response_type is missing

        :raises authorizationresponse.UnsupportedResponseType:
            If the response_type is not supported
        """
        response_type = self.request.query.get('response_type')
        if not response_type:
            raise authorizationresponse.InvalidRequest(self.redirect_uri, self.state)
        if response_type not in SUPPORTED_RESPONSE_TYPES:
            raise authorizationresponse.UnsupportedResponseType(self.redirect_uri, self.state)
        untrusted_client = self.clientregistry[self.client_id].secret is None
        if untrusted_client and response_type != 'token':
            raise authorizationresponse.UnauthorizedClient(self.redirect_uri, self.state)
        return response_type

    @decorators.reify
    def scope(self):
        """ The scope for this request. (OPTIONAL)

        :raises authorizationresponse.InvalidScope:
            If the scope is invalid
        """
        try:
            scopes = types.ScopeTokenSet(self.request.query.get('scope', ''))
        except ValueError:  # raised when malformed
            raise authorizationresponse.InvalidScope(self.redirect_uri, self.state)
        if not scopes <= self.scoperegistry:
            raise authorizationresponse.InvalidScope(self.redirect_uri, self.state)
        return scopes
