import logging
from json import loads as json_loads
import re
import typing as T

from aiohttp import web
from rest_utils import etag_from_int, assert_preconditions

from oauth2 import view
from . import _roles


_logger = logging.getLogger(__name__)
_ACCOUNTS = {
    'p.van.beek@amsterdam.nl': ['EMPLOYEE', 'EMPLOYEE_PLUS'],
    'e.lammerts@amsterdam.nl': ['EMPLOYEE'],
    'loetje.hanglip@amsterdam.nl': []
}


async def account_names_with_role(role: str):
    return [
        account_name for account_name, account in _ACCOUNTS.items() if role in account
    ]


class Accounts(view.OAuth2View):

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # TODO: implement

    @property
    def link_title(self):
        return "ADW accounts"

    async def accounts(self):
        return [
            Account(
                self.request,
                {'account': name},
                self.embed.get('item')
            )
            for name in _ACCOUNTS
        ]

    async def _links(self):
        return {'item': await self.accounts()}


class Account(view.OAuth2View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._roles = _ACCOUNTS.get(self['account'])

    @property
    def link_name(self):
        return self['account']

    @property
    def link_title(self):
        return "ADW account with email address <%s>" % self['account']

    @property
    def etag(self):
        if self._roles is None:
            return None
        return etag_from_int(hash(tuple(self._roles)))

    async def roles(self):
        return [
            _roles.Role(
                self.request,
                {'role': role_name},
                self.embed.get('roles')
            ) for role_name in await self.role_names()
        ]

    async def role_names(self) -> T.List[str]:
        return self._roles or []

    async def _links(self):
        if self._roles is None:
            raise web.HTTPNotFound()
        return {
            'role': await self.roles()
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
