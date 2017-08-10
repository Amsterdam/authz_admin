import importlib

from aiohttp import web

from oauth2 import clientregistry
from oauth2.config import load as config_load, all_scopes
from . import handler

from aiohttp.web import Application


def idpregistry(service_conf):
    # language=rst
    """Create an index of IdP plugins based on the given configuration.

    :return dict: IDP_ID => tuple(callable, callable)

    """
    idps = dict()
    for idp_mod in service_conf['idps']:
        idp = importlib.import_module("oauth2.idps.%s" % idp_mod)
        idps[idp.IDP_ID] = idp.get(service_conf['idps'][idp_mod])
    return idps


def start():
    # language=rst
    """Start the server."""
    config = config_load()
    service_conf = config['authz_service']
    # create application
    app = Application()
    # create request handler
    requesthandler = handler.RequestHandler(
        idpregistry(service_conf),
        clientregistry.get(),
        all_scopes(config)
    )
    # register resources
    root = service_conf['root_path']
    app.router.add_get(root + '/authorize', requesthandler.authorization)
    app.router.add_get(root + '/idps/{idp}', requesthandler.idp_callback)
    # run server
    web.run_app(app, host=service_conf['bind_host'], port=service_conf['bind_port'])

if __name__ == '__main__':
    start()
