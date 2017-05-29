import sys

from aiohttp import web

from oauth2 import config


def _build_application():
    return web.Application()


def main():
    # language=rst
    """
    The entry point of the authorization administration service.

    :returns int: the exit status of the process. See
        also the ``console_scripts`` in :file:`setup.py`.

    """
    SERVICE_CONFIG = config.get()['authz_admin_service']
    # create application
    app = _build_application()
    # run server
    web.run_app(
        app,
        host=SERVICE_CONFIG['host'],
        port=SERVICE_CONFIG['port']
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
