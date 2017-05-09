from aiohttp import web

from oauth2 import config
from . import routes


def start():
    conf = config.load()
    service_conf = conf['authorization_service']
    # create application
    app = web.Application()
    # register routes
    routes.setup_routes(app, service_conf['root'])
    # run server
    web.run_app(
        app,
        host=service_conf['host'],
        port=service_conf['port']
    )

if __name__ == '__main__':
    start()
