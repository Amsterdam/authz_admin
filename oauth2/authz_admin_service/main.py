from aiohttp import web

from oauth2.config import load as load_config


def start():
    config = load_config()
    service_config = config['authz_admin_service']
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
