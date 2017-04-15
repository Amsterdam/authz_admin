"""
    oauth2.server
    ~~~~~~~~~~~~~

    Some temporary decisions:

    * TOKEN TYPE
      For now we use the bearer token type. I've seen two alternatives; MAC
      access auth (never made it past draft RFC), comparable to HTTP digest
      authentication, and SAML 2.0 Bearer Assertion. The latter allows clients
      (or maybe even resource owners?) to obtain an Assertion that then can
      be used for client authentication or as authorization grant.
"""
from aiohttp import web
