import logging
import re
from json import loads as json_loads

from aiohttp import web

from authz_admin import database, view
from rest_utils import etag_from_int, assert_preconditions
from . import _roles

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
        role_ids = self.request.query.get('roles')
        if role_ids is not None:
            role_ids = role_ids.split(',')
            for role_id in role_ids:
                if not re.match(r'\w{1,32}$', role_id):
                    raise web.HTTPBadRequest(
                        text="Syntax error in query parameter 'roles'."
                    )
        if self.__cached_accounts is None:
            self.__cached_accounts = list([
                Account(
                    self.request,
                    {'account': row['account_id']},
                    self.embed.get('item'),
                    data=row
                )
                async for row in database.accounts(self.request, role_ids)
            ])
        return self.__cached_accounts

    async def _links(self):
        return {'item': await self.accounts()}


class Account(view.OAuth2View):

    def __init__(self, *args, data=False, **kwargs):
        super().__init__(*args, **kwargs)
        self._data = data

    async def data(self):
        if self._data is False:
            self._data = await database.account(self.request, self['account'])
        return self._data

    @property
    def link_name(self):
        return self['account']

    @property
    def link_title(self):
        return "ADW account voor <%s>" % self['account']

    async def etag(self):
        data = await self.data()
        if data is None:
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
        existing_roles = set(self.request.app['config']['authz_admin']['roles'].keys())
        try:
            roles = request_body_json['_links']['role']
            assert isinstance(roles, list)
        except:
            raise web.HTTPBadRequest(
                text="No '#/_links/role' array in request."
            ) from None
        new_roles = set()
        try:
            for link_object in roles:
                role = web.URL(link_object['href']).name
                assert role in existing_roles
                new_roles.add(role)
        except:
            raise web.HTTPBadRequest(
                text="Not all roles are valid HALJSON link objects to an existing role."
            ) from None

        if await self.data() is None:
            log_id = await database.create_account(self.request, self['account'], new_roles)
            status = 201
            headers = {
                'Location': self.rel_url.raw_path,
                'ETag': etag_from_int(log_id)
            }
        else:
            log_id = await database.update_account(self.request, self, new_roles)
            status = 204
            headers = {'ETag': etag_from_int(log_id)}
        return web.Response(status=status, headers=headers)

    async def delete(self) -> web.Response:
        assert_preconditions(
            self.request,
            await self.etag(),
            require_if_match=True
        )
        await database.delete_account(self.request, self)
        return web.Response(status=204)
