import asyncio
import logging
import os.path
import sys
import typing as T

import swagger_parser
import uvloop
from aiohttp import web

import rest_utils
from oauth2 import database
from oauth2.config import load as load_config
from . import handlers

_logger = logging.getLogger(__name__)


def add_routes(router):
    # language=rst
    """

    :param web.UrlDispatcher router:

    """
    handlers.Root.add_to_router(router, '/')
    handlers.Datasets.add_to_router(router, '/datasets')
    handlers.Dataset.add_to_router(router, '/datasets/{dataset}')
    handlers.Scopes.add_to_router(router, '/datasets/{dataset}/scopes')
    handlers.Scope.add_to_router(router, '/datasets/{dataset}/scopes/{scope}')


def on_response_prepare(request: web.Request, response: web.Response):
    _logger.debug("on_response_prepare() called.")
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
    config = load_config()
    app['config'] = config
    app['etag'] = rest_utils.ETagGenerator().update(config).etag
    app['connection_pool'] = database.ConnectionPool(config['postgres'])
    swagger_path = os.path.join(os.path.dirname(__file__), 'openapi.yml')
    _logger.debug("Loading swagger file '%s'", swagger_path)
    app['swagger'] = swagger_parser.SwaggerParser(
        swagger_path=swagger_path
    )
    app.router.add_static('/hal', 'hal-browser')
    add_routes(app.router)
    app.on_startup.append(database.put_schema)
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
        host=SERVICE_CONFIG['bind_host'],
        port=SERVICE_CONFIG['bind_port']
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
