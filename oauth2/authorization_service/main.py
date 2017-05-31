import importlib

from aiohttp import web

from oauth2 import clientregistry, scopes
from oauth2.config import get as config_get
from . import handler

from aiohttp.web import Application


def idpregistry(service_conf):
    """Create an index of IdP plugins based on the gievn configuration.

    :return dict: IDP_ID => tuple(callable, callable)

    """
    idps = dict()
    for idp_mod in service_conf['idp_config']:
        idp = importlib.import_module(idp_mod)
        idps[idp.IDP_ID] = idp.get(service_conf['idp_config'][idp_mod])
    return idps


def start():
    """Start the server."""
    config = config_get()
    service_conf = config['authorization_service']
    # create application
    app = Application()
    # create request handler
    requesthandler = handler.RequestHandler(
        idpregistry(service_conf),
        clientregistry.get(),
        scopes.all_scopes()
    )
    # register routes
    root = service_conf['root_path']
    app.router.add_get(root + '/authorize', requesthandler.authorization)
    app.router.add_get(root + '/idps/{idp}', requesthandler.idp_callback)
    # run server
    web.run_app(app, host=service_conf['bind_host'], port=service_conf['bind_port'])

if __name__ == '__main__':
    start()
