"""
    oauth2.rfc6749.authorizationrequest
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements the OAuth2 authorization request as defined in
    RFC6749. It extends aiohttp.web.Request with the authorization request
    properties related to the Authorization request, including input validation.
    It implements sections:

    * `3.1. Authorization Endpoint
       <https://tools.ietf.org/html/rfc6749#section-3.1>`_
    * `4.1.1. / 4.2.1  Authorization Request
       <https://tools.ietf.org/html/rfc6749#section-4.1.1>`_
    * `4.1.2.1 / 4.2.2.1 Error Response
       <https://tools.ietf.org/html/rfc6749#section-4.1.2.1>`_

    Usage:

        from rfc6749 import authorizationrequest

        @authorizationrequest(
            clientregistry=clientregistry, known_scopes=scoperegistry
        )
        async def my_aiohttp_view(request):
            request.state, request.redirect_uri, ... # etc
"""
import functools
import urllib

from aiohttp import web, web_exceptions

from . import types

SUPPORTED_RESPONSE_TYPES = {'code', 'flow'}


def authorizationrequest(clientregistry=None, known_scopes=None):
    """ Returns a decorator that can be used to turn a view into one that
    supports an OAuth2 authorization request.

    :param flows: the flows that this view supports (token, code, ..)
    """
    def decorator(f):
        """ Any view function decorated with this decorator will be called with
        an AuthorizationRequest instance as its single argument.
        """
        @functools.wraps(f)
        def wrapper(request):
            request.__class__ = AuthorizationRequest
            request.clientregistry = clientregistry
            request.known_scopes = known_scopes
            return f(request)
        return wrapper
    return decorator


class ErrorResponse(web_exceptions.HTTPFound):
    """ Base class for error responses.

    From RFC6749 section 4.1.2.1 and 4.2.2.1:

        If the request fails due to a missing, invalid, or mismatching
        redirection URI, or if the client identifier is missing or invalid,
        the authorization server SHOULD inform the resource owner of the
        error and MUST NOT automatically redirect the user-agent to the
        invalid redirection URI.

        If the resource owner denies the access request or if the request
        fails for reasons other than a missing or invalid redirection URI,
        the authorization server informs the client by adding the following
        parameters to the fragment component of the redirection URI using the
        "application/x-www-form-urlencoded" format, per Appendix B:

        error
            REQUIRED.  A single ASCII [USASCII] error code from the
            following:

            invalid_request [...]
            unauthorized_client [...]
            access_denied [...]
            unsupported_response_type [...]
            invalid_scope [...]
            server_error [...]
            temporarily_unavailable

            Values for the "error" parameter MUST NOT include characters
            outside the set %x20-21 / %x23-5B / %x5D-7E.

        error_description
            OPTIONAL.  Human-readable ASCII [USASCII] text providing
            additional information, used to assist the client developer in
            understanding the error that occurred.
            Values for the "error_description" parameter MUST NOT include
            characters outside the set %x20-21 / %x23-5B / %x5D-7E.

        error_uri
            OPTIONAL.  A URI identifying a human-readable web page with
            information about the error, used to provide the client
            developer with additional information about the error.
            Values for the "error_uri" parameter MUST conform to the
            URI-reference syntax and thus MUST NOT include characters
            outside the set %x21 / %x23-5B / %x5D-7E.

        state
            REQUIRED if a "state" parameter was present in the client
            authorization request.  The exact value received from the
            client.

    We use the RFC's error code description as the value for error_description,
    and for now we don't include an error_uri.
    """

    def __init__(self, request, params):
        """ Creates a new error response, including the state parameter if it
        was present in the request.
        """
        redir_uri = request.redirect_uri
        if request.state is not None:
            params['state'] = request.state
        super().__init__(redir_uri + '#' + urllib.parse.urlencode(params))

    @classmethod
    def invalid_request(cls, request):
        params = {
            'error': 'invalid_request',
            'error_description': 'The request is missing a required parameter,'
                                 ' includes an invalid parameter value,'
                                 ' includes a parameter more than once, or is'
                                 ' otherwise malformed.'
        }
        return cls(request, params)

    @classmethod
    def unauthorized_client(cls, request):
        params = {
            'error': 'unauthorized_client',
            'error_description': 'The client is not authorized to request an'
                                 ' authorization code using this method.'
        }
        return cls(request, params)

    @classmethod
    def access_denied(cls, request):
        params = {
            'error': 'access_denied',
            'error_description': 'The resource owner or authorization server'
                                 ' denied the request.'
        }
        return cls(request, params)

    @classmethod
    def unsupported_response_type(cls, request):
        params = {
            'error': 'unsupported_response_type',
            'error_description': 'The authorization server does not support'
                                 ' obtaining an access token using this method.'
        }
        return cls(request, params)

    @classmethod
    def invalid_scope(cls, request):
        params = {
            'error': 'invalid_scope',
            'error_description': 'The requested scope is invalid, unknown, or'
                                 ' malformed.'
        }
        return cls(request, params)

    @classmethod
    def server_error(cls, request):
        params = {
            'error': 'server_error',
            'error_description': 'The authorization server encountered an'
                                 ' unexpected condition that prevented it from'
                                 ' fulfilling the request.'
        }
        return cls(request, params)

    @classmethod
    def temporarily_unavailable(cls, request):
        params = {
            'error': 'temporarily_unavailable',
            'error_description': 'The authorization server is currently unable'
                                 ' to handle the request due to a temporary'
                                 ' overloading or maintenance of the server.'
        }
        return cls(request, params)


class AuthorizationRequest(web.Request):
    """ Provides request parsing for an authorization request.

    Parmater specific comments can be found at the properties.

    This implementation aims to be compatible with RFC6749 section 3.1:

    * Parameters sent without a value MUST be treated as if they were omitted
        from the request.
    * The authorization server MUST ignore unrecognized request parameters.
    * Request and response parameters MUST NOT be included more than once.

    :todo
        How can we check whether a request parameter was included more than
        once? (point 3 above)
    """

    @property
    def client_id(self):
        """ Lazy property that returns the client_id included in the request.

        From RFC6749 section 4.1.1 and 4.2.1:

            client_id: REQUIRED. The client identifier as described in Section
            2.2.

        :raises aiohttp.web_exceptions.HTTPBadRequest: if the client_id query
            parameter is not present or invalid

        :todo
            Once we have settled on a format for the client identifier we can
            do more extensive checks.
        """
        try:
            return self._client_id
        except AttributeError:
            pass
        client_id = self.query.get('client_id', '').encode('ascii')
        if not client_id:
            raise web_exceptions.HTTPBadRequest(body='missing client_id')
        self._client_id = client_id
        return client_id

    @property
    def redirect_uri(self):
        """ Lazy property that returns the redirect_uri for this request.

        From RFC6749 section 4.1.1 and 4.2.1:

            redirect_uri: OPTIONAL if only one redirect endpoint was registered
            for this client, REQUIRED if more. As described in Section 3.1.2.

        :raises aiohttp.web_exceptions.HTTPBadRequest: if the redirect_uri
            parameter is not present, invalid, or mismatching.
        """
        try:
            return self._redirect_uri
        except AttributeError:
            pass
        client_redirects = self.client.redirect_uris
        redirect_uri = self.query.get('redirect_uri')
        # The below condition is valid but pretty tricky... treat with care
        if not redirect_uri and len(client_redirects) == 1:
            redirect_uri = client_redirects[0]
        elif redirect_uri not in client_redirects:
            raise web_exceptions.HTTPBadRequest(
                body='must provide valid redirect_uri'
            )
        self._redirect_uri = redirect_uri
        return redirect_uri

    @property
    def state(self):
        """ Property that returns the state parameter for this request.

        From RFC6749 section 4.1.1 and 4.2.1:

            state: RECOMMENDED.  An opaque value used by the
            client to maintain state between the request and callback. The
            authorization server includes this value when redirecting the user-
            agent back to the client.  The parameter SHOULD be used for
            preventing cross-site request forgery as described in Section 10.12.

        """
        return self.query.get('state')

    @property
    def response_type(self):
        """ Lazy property that returns the response_type for this request.

        From RFC6749 section 4.1.1 and 4.2.1:

            response_type: REQUIRED. Value MUST be set to "token" for an
            implicit grant, or to "code" for an authorization code grant.

        :raises ErrorResponse:
            If the response_type is missing or not supported.
        """
        try:
            return self._response_type
        except AttributeError:
            pass
        response_type = self.query.get('response_type')
        if not response_type:
            raise ErrorResponse.invalid_request(self)
        if response_type not in SUPPORTED_RESPONSE_TYPES:
            raise ErrorResponse.unsupported_response_type(self)
        self._response_type = response_type
        return response_type

    @property
    def scope(self):
        """ Lazy property that returns the scope for this request.

        From RFC6749 section 4.1.1 and 4.2.1:

            scope: OPTIONAL. The scope of the access request as described by
            Section 3.3.

        :raises ErrorResponse:
            If the scope is invalid
        """
        try:
            return self._scope
        except AttributeError:
            pass
        try:
            scope = types.ScopeTokenSet(self.query.get('scope', ''))
        except ValueError:  # raised when malformed
            raise ErrorResponse.invalid_scope(self)
        if not scope <= self.known_scopes:
            raise ErrorResponse.invalid_scope(self)
        self._scope = scope
        return scope

    @property
    def client(self):
        """ Lazy property that returns the client that made this request.
        """
        try:
            return self._client
        except AttributeError:
            pass
        if self.client_id not in self.clientregistry:
            raise web_exceptions.HTTPBadRequest(body='unknown client id')
        self._client = self.clientregistry[self.client_id]
        return self._client

    @property
    def clientregistry(self):
        """ Placeholder for the client registry. An implementation must provide
        one using the setter for this property:

            request.clientregistry = my_clientregistry

        A client registry must be a mapping of client_identifiers as keys
        """
        try:
            return self._clientregistry
        except AttributeError:
            raise AttributeError('Must provide a clientregistry')

    @clientregistry.setter
    def clientregistry(self, registry):
        self._clientregistry = registry

    @property
    def known_scopes(self):
        """ Placeholder for the scope registry. An implementation must provide
        one using the setter for this property:

            request.scoperegistry = my_scoperegistry

        A scope registry must be a mapping with scope names as keys
        """
        try:
            return self._scoperegistry
        except AttributeError:
            raise AttributeError('Must provide a clientregistry')

    @known_scopes.setter
    def known_scopes(self, registry):
        self._scoperegistry = registry
