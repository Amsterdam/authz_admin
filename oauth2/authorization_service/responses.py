"""
    oauth2.authorization_service.responses
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from aiohttp import web


def authorization_implicit_grant(client_id, redirect_uri, scope, state):
    return web.HTTPSeeOther(redirect_uri)
