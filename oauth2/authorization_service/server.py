import importlib

from aiohttp import web

from oauth2 import config, clientregistry, scoperegistry
from . import handler


def register_routes(app, root, requesthandler):
    """ Register all resources.
    """
    app.router.add_get(
        root + '/authorize', requesthandler.authorization)
    app.router.add_get(
        root + '/idps/{idp}', requesthandler.idp_callback, name='idp-callback')


def idpregistry(conf):
    """ Create an index of IdP plugins based on the gievn configuration.

    :param conf: configuration dict
    :return dict: IDP_ID => tuple(callable, callable)
    """
    idps = dict()
    for idp_mod in conf['idp']:
        idp = importlib.import_module(idp_mod)
        idps[idp.IDP_ID] = idp.get(conf['idp'][idp_mod])
    return idps


def start():
    """ Loads the config and start the server
    """
    conf = config.load()
    service_conf = conf['authorization_service']
    # create application
    app = web.Application()
    # create request handler
    requesthandler = handler.RequestHandler(
        idpregistry(conf),
        clientregistry.get(),
        scoperegistry.get(),
        service_conf
    )
    # register routes
    register_routes(app, service_conf['root'], requesthandler)
    # run server
    web.run_app(
        app,
        host=service_conf['host'],
        port=service_conf['port']
    )

if __name__ == '__main__':
    start()
