"""
    oauth2.authorization_service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Some decisions:

    * STATE

      The state parameter is optional in the RFC, but we require it.

    * TOKEN TYPE

      For now we use the bearer token type. I've seen two alternatives; MAC
      access auth (never made it past draft RFC), comparable to HTTP digest
      authentication, and SAML 2.0 Bearer Assertion. The latter allows clients
      (or maybe even resource owners?) to obtain an Assertion that then can
      be used for client authentication or as authorization grant.

    * REDIRECT URIs

      For now we only allow exact matches of redirect URIs. We may want to
      allow registering partial URIs, for example only a hostname (like
      example.com), and parse the redirect_uri given at the endpoints. Parsing
      URIs is however not trivial to do securely.

      We will use HTTP 303 See Other for all redirects. This should ensure
      that all redirects result in GET requests, also when it results from a
      POST. According to RFC 2616, pre-HTTP/1.1 user-agents do not understand
      this status. We could also choose to use 302 instead, which is said to
      behave like a 303 on most user-agents.

      For now we check that redurect_uris do not contain reserved query
      components during client registration. This is safe under the assumption
      that the registered redirects are safe against tampering. Further more,
      this method only holds as long as we only allow exact matches. Later on
      way me want to check the URI before redirecting, or possibly even at both
      points in time.
"""
