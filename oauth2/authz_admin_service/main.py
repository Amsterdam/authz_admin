import sys
import asyncio
import uvloop
import os.path
import logging

from aiohttp import web
import swagger_parser

from rest_utils.middleware import middleware as rest_utils_middleware
from oauth2.config import load as load_config
from oauth2 import database
from . import handlers

_logger = logging.getLogger(__name__)


def add_routes(router):
    # language=rst
    """

    :param web.UrlDispatcher router:

    """
    handlers.Root.add_to_router(router, '/')
    handlers.Datasets.add_to_router(router, '/datasets/')
    handlers.Dataset.add_to_router(router, '/datasets/{dataset}')


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
            rest_utils_middleware,
            web.normalize_path_middleware()
        ]
    )
    config = load_config()
    app['config'] = config
    app['connection_pool'] = database.ConnectionPool(config['postgres'])
    app['rest_utils.swagger'] = swagger_parser.SwaggerParser(
        swagger_path=os.path.join(os.path.dirname(__file__), 'openapi.yml')
    )
    add_routes(app.router)
    app.on_startup.append(database.put_schema)
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
