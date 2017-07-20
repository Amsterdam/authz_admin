import sys
import asyncio
import uvloop

from aiohttp import web
from rest_utils import parse_embed
import rest_utils.resources as rest_resources

from oauth2.config import load as load_config
from oauth2 import database
from . import resources


def add_routes(router):
    # language=rst
    """

    :param web.UrlDispatcher router:

    """
    root = router.add_resource('/', name='root')
    rest_resources.DumbCollection(root)
    datasets = router.add_resource('/datasets/', name='datasets')
    rest_resources.DumbCollection(datasets)



# noinspection PyUnusedLocal
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
            parse_embed.middleware,
            web.normalize_path_middleware()
        ]
    )
    config = load_config()
    app['config'] = config
    app['connection_pool'] = database.ConnectionPool(config['postgres'])
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
