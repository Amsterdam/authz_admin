import asyncio
import logging
import os.path
import sys
import re

import aiohttp_jinja2
import jinja2
import swagger_parser
import uvloop
from aiohttp import web

import rest_utils
from oauth2 import config

_logger = logging.getLogger(__name__)


async def authenticate_get_handler(request: web.Request):
    """Performs HTTP Basic Auth."""
    response = web.Response()
    return response


async def authenticate_post_handler(request):
    response = web.Response()
    return response


@aiohttp_jinja2.template('login.html')
async def login(request: web.Request) -> dict:
    return {
        'action_url': 'authenticate?' + request.query_string,
        'whitelisted': False,
        'html_error': None
    }


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
            rest_utils.middleware
        ]
    )
    app['config'] = config.load()
    swagger_path = os.path.join(os.path.dirname(__file__), 'openapi.yml')
    _logger.info("Loading swagger file '%s'", swagger_path)
    app['swagger'] = swagger_parser.SwaggerParser(
        swagger_path=swagger_path
    )
    app['prefix'] = app['swagger'].base_path
    app.router.add_route('GET', app['prefix'] + '/login', login)
    app.router.add_route('GET', app['prefix'] + '/authenticate', authenticate_get_handler)
    app.router.add_route('POST', app['prefix'] + '/authenticate', authenticate_post_handler)
    app.router.add_static(app['prefix'] + '/static', 'oauth2/authn_service/static')
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

    aiohttp_jinja2.setup(
        app, loader=jinja2.PackageLoader('oauth2.authn_service')
    )

    # run server
    host = re.fullmatch(r'(.*?):(\d+)', app['swagger'].specification['host'])
    assert host, "Host not defined in swagger file."
    web.run_app(
        app,
        host=host[1],
        port=int(host[2])
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
