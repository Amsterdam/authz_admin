"""
    oauth2.authorization_service.responses
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from aiohttp import web


def authorization_implicit_grant(request):
    return web.HTTPSeeOther(request.redirect_uri)
