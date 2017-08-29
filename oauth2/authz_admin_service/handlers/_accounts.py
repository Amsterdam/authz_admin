import logging
from json import loads as json_loads
import re
import typing as T

from aiohttp import web
from rest_utils import etag_from_int, assert_preconditions
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


async def account_names_with_role(role: str):
    return [
        account_name for account_name, account in _ACCOUNTS.items() if role in account
    ]


class Accounts(view.OAuth2View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__cached_accounts = None

    @property
    def link_title(self):
        return "ADW accounts"

    async def accounts(self):
        if self.__cached_accounts is None:
            app = self.request.app
            metadata: sa.MetaData = app['metadata']
            async with app['engine'].acquire() as conn:
                self.__cached_accounts = [
                    Account(
                        self.request,
                        {'account': row['id_from_idp']},
                        self.embed.get('item'),
                        row=row
                    )
                    async for row in conn.execute(sa.select([metadata.tables['Accounts']]))
                ]
        return self.__cached_accounts

    async def _links(self):
        return {'item': await self.accounts()}


class Account(view.OAuth2View):

    def __init__(self, *args, row=None, **kwargs):
        super().__init__(*args, **kwargs)
        if row is None:
            self._id = None
            # self._id_from_idp = None
            # self._audit_id = None
        else:
            self._id = row['id']
            self._id_from_idp = row['id_from_idp']
            self._audit_id = row['audit_id']
        self._roles = None

    async def id(self):
        if self._id is None:
            app = self.request.app
            table_accounts = app['metadata'].tables['Accounts']
            async with app['engine'].acquire() as conn:
                rows = await conn.execute(
                    sa.select([table_accounts]).where(table_accounts.c.id_from_idp == self['account'])
                )
                row = await rows.fetchone()
                if row is None:
                    raise web.HTTPNotFound()
                self._id = row['id']
                self._id_from_idp = row['id_from_idp']
                self._audit_id = row['audit_id']
        return self._id

    async def id_from_idp(self):
        await self.id()
        return self._id_from_idp

    async def audit_id(self):
        await self.id()
        return self._audit_id

    async def roles(self) -> T.Set[T.Dict]:
        id = await self.id()
        if self._roles is None:
            app = self.request.app
            table_accountroles = app['metadata'].tables['AccountRoles']
            async with app['engine'].acquire() as conn:
                self._roles = set([
                    {
                        'id': row['id'],
                        'role_id': row['role_id'],
                        'grounds': row['grounds'],
                        'audit_id': row['audit_id']
                    } async for row in conn.execute(
                        sa.select([table_accountroles])
                        .where(table_accountroles.c.account_id == id)
                    )
                ])
        return self._roles

    @property
    def link_name(self):
        return self['account']

    @property
    def link_title(self):
        return "ADW account with email address <%s>" % self['account']

    @property
    def etag(self):
        try:
            return etag_from_int(hash(self.roles()))
        except web.HTTPNotFound:
            return None

    async def _links(self):
        if self._roles is None:
            raise web.HTTPNotFound()
        return {
            'role': [
                _roles.Role(
                    self.request,
                    {'role': role['role_id']},
                    self.embed.get('role')
                ) for role in await self.roles()
            ]
        }

    async def put(self):
        if_match = self.request.headers.get('if-match', '')
        if_none_match = self.request.headers.get('if-none-match', '')
        if if_match == '' and if_none_match == '':
            raise web.HTTPPreconditionRequired()
        assert_preconditions(self.request, self.etag)
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
        assert_preconditions(self.request, self.etag)
        del _ACCOUNTS[self['account']]
        return web.Response(status=204)

class AccountRole(view.OAuth2View):

    def __init__(self, *args, row=None, **kwargs):
        super().__init__(*args, **kwargs)
        if row is None:
            pass
        else:
            pass

    @property
    def link_title(self):
        return self['role']

    async def accounts(self):
        if self.__cached_accounts is None:
            app = self.request.app
            metadata: sa.MetaData = app['metadata']
            async with app['engine'].acquire() as conn:
                self.__cached_accounts = [
                    Account(
                        self.request,
                        {'account': row['id_from_idp']},
                        self.embed.get('item'),
                        row=row
                    )
                    async for row in conn.execute(sa.select([metadata.tables['Accounts']]))
                ]
        return self.__cached_accounts

    async def _links(self):
        return {'item': await self.accounts()}


