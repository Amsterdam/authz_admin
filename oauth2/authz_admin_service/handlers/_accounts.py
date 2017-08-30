import logging
from json import loads as json_loads
import re
import typing as T

from aiohttp import web
from rest_utils import etag_from_int, assert_preconditions, ETagGenerator
import sqlalchemy as sa

from oauth2 import view
from . import _roles
from .. import database


_logger = logging.getLogger(__name__)
_ACCOUNTS = {
    'p.van.beek@amsterdam.nl': ['CDE', 'CDE_PLUS'],
    'e.lammerts@amsterdam.nl': ['CDE'],
    'loetje.hanglip@amsterdam.nl': []
}


class Accounts(view.OAuth2View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__cached_accounts = None

    @property
    def link_title(self):
        return "ADW accounts"

    async def accounts(self):
        if self.__cached_accounts is None:
            self.__cached_accounts = list([
                Account(
                    self.request,
                    {'account': row['account_id']},
                    self.embed.get('item'),
                    data=row
                )
                async for row in database.accounts(self.request)
            ])
        return self.__cached_accounts

    async def _links(self):
        return {'item': await self.accounts()}


class Account(view.OAuth2View):

    def __init__(self, *args, data=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = data

    async def data(self):
        if self._data is None:
            self._data = await database.account(self.request, self['account'])
        if self._data is None:
            raise web.HTTPNotFound()
        return self._data

    @property
    def link_name(self):
        return self['account']

    @property
    def link_title(self):
        return "ADW account voor <%s>" % self['account']

    async def etag(self):
        try:
            data = await self.data()
        except web.HTTPNotFound:
            return None
        return etag_from_int(data['log_id'])

    async def _links(self):
        data = await self.data()
        return {
            'role': [
                _roles.Role(
                    self.request,
                    {'role': role_id},
                    self.embed.get('role')
                ) for role_id in data['role_ids']
            ]
        }

    async def put(self):
        if_match = self.request.headers.get('if-match', '')
        if_none_match = self.request.headers.get('if-none-match', '')
        if if_match == '' and if_none_match == '':
            raise web.HTTPPreconditionRequired()
        assert_preconditions(self.request, await self.etag())
        if not re.match(r'application/(?:hal\+)?json(?:$|;)',
                        self.request.content_type):
            raise web.HTTPUnsupportedMediaType()
        try:
            request_body_json = json_loads(await self.request.text())
        except:
            raise web.HTTPBadRequest()
        # self.request.app['swagger'].validate_definition('Account', request_body_json)
        existing_roles = set(self.request.app['config']['authz_admin_service']['roles'].keys())
        try:
            roles = request_body_json['_links']['role']
            assert isinstance(roles, list)
        except:
            raise web.HTTPBadRequest(
                text="No '#/_links/role' array in request."
            )
        new_roles = set()
        try:
            for link_object in roles:
                role = web.URL(link_object['href']).name
                assert role in existing_roles
                new_roles.add(role)
        except:
            raise web.HTTPBadRequest(
                text="Not all roles are valid HALJSON link objects to an existing role."
            )
        status_code = 204 if self['account'] in _ACCOUNTS else 201
        _ACCOUNTS[self['account']] = new_roles
        response_headers = {} if status_code == 204 else \
            {'Location': self.rel_url.raw_path}
        return web.Response(status=status_code, headers=response_headers)

    async def delete(self) -> web.Response:
        if_match = self.request.headers.get('if-match', '')
        if if_match == '':
            raise web.HTTPPreconditionRequired()
        assert_preconditions(self.request, await self.etag())
        del _ACCOUNTS[self['account']]
        return web.Response(status=204)
