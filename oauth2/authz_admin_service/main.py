import asyncio
import logging
import math
import os.path
import re
import sys
import time

import jwt
import swagger_parser
import uvloop
from aiohttp import web

import rest_utils
from oauth2 import config
from . import handlers

_logger = logging.getLogger(__name__)


def access_token(scope: str, secret) -> bytes:
    return jwt.encode({
        'sub': 'dp:datapunt@amsterdam.nl',
        'iat': math.floor(time.time()) - 5,
        'exp': math.floor(time.time()) + 3600 * 12,
        'scope': scope
    }, secret)


async def authorization_handler(request: web.Request) -> web.Response:
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
    _logger.debug("location: %s", location)
    return web.Response(
        status=302,
        headers={
            'Location': str(location)
        }
    )


def add_routes(app: web.Application):
    base_path = app['swagger'].base_path
    app.router.add_static(base_path + '/swagger-ui', 'swagger-ui/dist', follow_symlinks=True)
    app.router.add_route('GET', base_path + '/authorization', authorization_handler, name='authorization')
    handlers.Root.add_to_router(app.router, base_path + '/')
    handlers.Accounts.add_to_router(app.router, base_path + '/accounts')
    handlers.Account.add_to_router(app.router, base_path + '/accounts/{account}')
    handlers.Datasets.add_to_router(app.router, base_path + '/datasets')
    handlers.Dataset.add_to_router(app.router, base_path + '/datasets/{dataset}')
    handlers.Scope.add_to_router(app.router, base_path + '/datasets/{dataset}/{scope}')
    handlers.Profiles.add_to_router(app.router, base_path + '/profiles')
    handlers.Profile.add_to_router(app.router, base_path + '/profiles/{profile}')
    handlers.Roles.add_to_router(app.router, base_path + '/roles')
    handlers.Role.add_to_router(app.router, base_path + '/roles/{role}')


def on_response_prepare(request: web.Request, response: web.Response):
    response.headers.add('Access-Control-Allow-Origin', '*')


def application(argv):
    # language=rst
    """Constructs and returns an `aiohttp.web.application`.

    :param list argv: Unused, but required to allow this method to be called by
        the aiohttp :ref:`aiohttp-web-cli`.

    """
    if len(argv) > 0:
        raise Exception("Don’t know what to do with command line parameters.", argv)
    app = web.Application(
        middlewares=[
            rest_utils.middleware,
            web.normalize_path_middleware()
        ]
    )
    app['config'] = config.load()
    app['etag'] = rest_utils.ETagGenerator().update(app['config']).etag
    swagger_path = os.path.join(os.path.dirname(__file__), 'openapi.yml')
    _logger.info("Loading swagger file '%s'", swagger_path)
    app['swagger'] = swagger_parser.SwaggerParser(
        swagger_path=swagger_path
    )
    add_routes(app)
    app.on_response_prepare.append(on_response_prepare)
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
    SERVICE_CONFIG = app['config']['authz_admin_service']
    web.run_app(
        app,
        port=SERVICE_CONFIG['bind_port']
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
