import logging
from json import loads as json_loads
import re

from aiohttp import web
import jsonschema

from oauth2 import view
from rest_utils import etag_from_int, assert_preconditions

from ._roles import Role


_logger = logging.getLogger(__name__)
_ACCOUNTS = {
    'p.van.beek@amsterdam.nl': ['EMPLOYEE', 'EMPLOYEE_PLUS'],
    'e.lammerts@amsterdam.nl': ['EMPLOYEE'],
    'loetje.hanglip@amsterdam.nl': []
}


class Accounts(view.OAuth2View):

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # TODO: implement

    @property
    def link_title(self):
        return "ADW accounts"

    async def _links(self):
        items = [
            Account(
                self.request,
                {'account': name},
                self.embed.get('item')
            )
            for name in _ACCOUNTS
        ]
        return {'item': items}


class Account(view.OAuth2View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._account = _ACCOUNTS.get(self['account'])

    @property
    def link_name(self):
        return self['account']

    @property
    def link_title(self):
        return "Account '%s'" % self['account']

    @property
    def etag(self):
        if self._account:
            return etag_from_int(hash(tuple(self._account)))
        return False

    async def _links(self):
        if self._account is None:
            raise web.HTTPNotFound()
        return {
            'role': [
                Role(
                    self.request,
                    {'role': name},
                    self.embed.get('roles')
                ) for name in self._account
            ]
        }

    async def put(self):
        if ('if-match' not in self.request.headers and
                'if-none-match' not in self.request.headers):
            raise web.HTTPPreconditionRequired()
        assert_preconditions(self.request, self.etag)
        if not re.match(r'application/(?:hal\+)json(?:$|;)',
                        self.request.content_type):
            raise web.HTTPUnsupportedMediaType()
        try:
            request_body_json = json_loads(self.request.text())
        except:
            raise web.HTTPBadRequest()
        # self.request.app['swagger'].validate_definition('Account', request_body_json)
        raise web.HTTPNotImplemented
