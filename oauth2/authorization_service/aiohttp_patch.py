""" Patch for aiohttp that introduces scheme and host resolution based on
common headers added by proxies.
"""
import re
from multidict import istr

from aiohttp import hdrs, web, helpers
from yarl import URL


class Request(web.Request):

    HDR_FORWARDED = istr('FORWARDED')
    HDR_X_FORWARDED_PROTO = istr('X-FORWARDED-PROTO')
    HDR_X_FORWARDED_HOST = istr('X-FORWARDED-HOST')

    @helpers.reify
    def _forwarded(self):
        forwarded = self._message.headers.get(self.HDR_FORWARDED)
        if forwarded is not None:
            pattern = r'^by=([^;]*); +for=([^;]*); +host=([^;]*); +proto=(https?)$'
            parsed = re.findall(pattern, forwarded)
            if parsed:
                return parsed[0]
        return None

    @helpers.reify
    def _scheme(self):
        proto = 'http'
        if self._transport.get_extra_info('sslcontext'):
            proto = 'https'
        elif self._forwarded:
            _, _, _, proto = self._forwarded
        elif self.HDR_X_FORWARDED_PROTO in self._message.headers:
            proto = self._message.headers[self.HDR_X_FORWARDED_PROTO]
        return proto

    @helpers.reify
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

    @helpers.reify
    def url(self):
        return URL('{}://{}{}'.format(
            self._scheme, self.host, str(self._rel_url)))


class Application(web.Application):
    def _make_request(self, message, payload, protocol, writer, task,
                      _cls=Request):
        return super()._make_request(message, payload, protocol, writer, task,
                                     _cls=Request)
