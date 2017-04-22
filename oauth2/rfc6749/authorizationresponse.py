"""
    oauth2.rfc6749.authorizationresponse
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module implements the OAuth2 authorization response as defined in
    RFC6749. It extends aiohttp.web.HTTPSeeOther, which is both an
    aiohttp.Response and an Exception. It implements sections:

    * `4.1.2. Authorization Response
       <https://tools.ietf.org/html/rfc6749#section-4.1.2>`_

    Usage:

        from rfc6749.authorization import AuthorizationResponse
"""
from aiohttp import web


class AuthorizationResponse(web.HTTPSeeOther):

    def __init__(self, redirect_uri, *args, **kwargs):
        self.redirect_uri = redirect_uri
        super().__init__(*args, **kwargs)
