import asyncio
import logging
import sys
import re
import time
import math

import uvloop
from aiohttp import web
import jwt

import rest_utils
from oauth2 import config

_logger = logging.getLogger(__name__)


def access_token(scope: str, secret) -> str:
    return jwt.encode({
        'sub': 'dp:datapunt@amsterdam.nl',
        'iat': math.floor(time.time()) - 5,
        'exp': math.floor(time.time()) + 3600 * 12,
        'scope': scope
    }, secret)


async def authorization_handler(request: web.Request):
    if (request.query.get('response_type') != 'token' or
            'redirect_uri' not in request.query):
        raise web.HTTPBadRequest(
            text="Response type isn't 'token' or no redirect URI provided."
        )
    if 'scope' in request.query:
        scope = request.query['scope']
        if not re.fullmatch(r'[\x21\x23-\x5a\x5e-\x7e\[\]]+(?: [\x21\x23-\x5a\x5e-\x7e\[\]]+)*', scope):
            raise web.HTTPBadRequest(
                text="Syntax error in 'scopes' query parameter."
            )
    else:
        _logger.debug("all_scopes: %s", config.all_scopes(request.app['config']))
        scope = ' '.join(config.all_scopes(request.app['config']))
    location = web.URL(request.query['redirect_uri'], strict=True)
    location = location.update_query(
        access_token=access_token(scope, 'test123').decode(),
        token_type='bearer',
        scope=scope
    )
    if 'state' in request.query:
        location = location.update_query(state=request.query['state'])
    return web.Response(
        status=302,
        headers={
            'Location': str(location)
        }
    )


def add_cors_headers(request: web.Request, response: web.Response):
    _logger.debug("on_response_prepare() called.")
    response.headers.add('Access-Control-Allow-Origin', '*')


def application(argv):
    # language=rst
    """Constructs and returns an `aiohttp.web.application`.

    :param list argv: Unused, but required to allow this method to be called by
        the aiohttp :ref:`aiohttp-web-cli`.

    """
    if len(argv) > 0:
        raise Exception("Don't know what to do with command line parameters.", argv)
    app = web.Application(
        middlewares=[
            rest_utils.middleware,
            web.normalize_path_middleware()
        ]
    )

    app['config'] = config.load()
    app.router.add_route('GET', '/authorization', authorization_handler)
    app.on_response_prepare.append(add_cors_headers)
    return app


def main():
    # language=rst
    """The entry point of the authorization administration service.

    :returns int: the exit status of the process. See
        also the ``console_scripts`` in :file:`setup.py`.

    """

    # Set UVLoop as our default event loop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # Build the application
    app = application([])

    # run server
    SERVICE_CONFIG = app['config']['authz_service']
    web.run_app(
        app,
        host=SERVICE_CONFIG['bind_host'],
        port=SERVICE_CONFIG['bind_port']
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
