from aiohttp import web

from oauth2 import config


def start():
    CONFIG = config.get()
    service_config = CONFIG['authz_admin_service']
    # create application
    app = web.Application()
    # run server
    web.run_app(
        app,
        host=service_config['host'],
        port=service_config['port'],
        path=service_config['root']
    )

if __name__ == '__main__':
    start()
