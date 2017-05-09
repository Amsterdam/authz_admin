from aiohttp import web

from oauth2 import config


def start():
    conf = config.load()
    service_conf = conf['scope_admin_service']
    # create application
    app = web.Application()
    # run server
    web.run_app(
        app,
        host=service_conf['host'],
        port=service_conf['port'],
        path=service_conf['root']
    )

if __name__ == '__main__':
    start()
