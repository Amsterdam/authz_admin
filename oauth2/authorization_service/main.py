import importlib
import re
from multidict import istr

from aiohttp import hdrs, web
from yarl import URL

from oauth2 import config, clientregistry, decorators, scopes
from . import handler, routes


class OAuth20Request(web.Request):

    HDR_FORWARDED = istr('FORWARDED')
    HDR_X_FORWARDED_PROTO = istr('X-FORWARDED-PROTO')
    HDR_X_FORWARDED_HOST = istr('X-FORWARDED-HOST')

    @decorators.reify
    def _forwarded(self):
        forwarded = self._message.headers.get(self.HDR_FORWARDED)
        if forwarded is not None:
            pattern = r'^by=([^;]*); +for=([^;]*); +host=([^;]*); +proto=(https?)$'
            parsed = re.findall(pattern, forwarded)
            if parsed:
                return parsed[0]
        return None

    @decorators.reify
    def _scheme(self):
        proto = 'http'
        if self._transport.get_extra_info('sslcontext'):
            proto = 'https'
        elif self._forwarded:
            _, _, _, proto = self._forwarded
        elif self.HDR_X_FORWARDED_PROTO in self._message.headers:
            proto = self._message.headers[self.HDR_X_FORWARDED_PROTO]
        return proto

    @decorators.reify
    def host(self):
        """ Hostname of the request.

        Hostname is resolved through the following headers, in this order:

        - Forwarded
        - X-Forwarded-Host
        - Host

        Will return str or None if no hostname is found in the headers.
        """
        host = None
        if self._forwarded:
            _, _, host, _ = self._forwarded
        elif self.HDR_X_FORWARDED_HOST in self._message.headers:
            host = self._message.headers[self.HDR_X_FORWARDED_HOST]
        elif hdrs.HOST in self._message.headers:
            host = self._message.headers[hdrs.HOST]
        return host

    @decorators.reify
    def url(self):
        return URL('{}://{}{}'.format(
            self._scheme, self.host, str(self._rel_url)))


class OAuth20Application(web.Application):
    def _make_request(self, message, payload, protocol, writer, task,
                      _cls=OAuth20Request):
        return super()._make_request(message, payload, protocol, writer, task,
                                     _cls=OAuth20Request)


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
    conf = config.get()
    service_conf = conf['authorization_service']
    # create application
    app = OAuth20Application()
    # create request handler
    requesthandler = handler.RequestHandler(
        idpregistry(conf),
        clientregistry.get(),
        scopes.get()
    )
    # register routes
    routes.register_routes(app, service_conf['root'], requesthandler)
    # run server
    web.run_app(
        app,
        host=service_conf['host'],
        port=service_conf['port']
    )

if __name__ == '__main__':
    start()
