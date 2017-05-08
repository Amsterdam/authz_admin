import importlib

from aiohttp import web

from oauth2 import config


def start_server():
    conf = config.load()
    server_conf = conf['server']
    # create main application
    app = web.Application()
    # load all subapps
    for appname, prefix in server_conf['subapps'].items():
        subapp = web.Application()
        routes = importlib.import_module('oauth2.{}.routes'.format(appname))
        routes.setup_routes(subapp)
        app.add_subapp('{}{}'.format(server_conf['root'], prefix), subapp)
    # run server
    web.run_app(app, host=server_conf['host'], port=server_conf['port'])

if __name__ == '__main__':
    start_server()
