import logging
from docutils.core import publish_parts

from aiohttp import web

from oauth2 import view
from . import _profiles, _accounts
from .. import database

_logger = logging.getLogger(__name__)


class Roles(view.OAuth2View):

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # TODO: implement

    async def etag(self):
        return self.request.app['etag']

    @property
    def link_title(self):
        return "ADW Rollen"

    async def _links(self):
        items = [
            Role(
                self.request,
                {'role': name},
                self.embed.get('item')
            )
            for name in self.request.app['config']['authz_admin_service']['roles']
        ]
        return {'item': items}


class Role(view.OAuth2View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        roles = self.request.app['config']['authz_admin_service']['roles']
        if self['role'] not in roles:
            raise web.HTTPNotFound()
        self._role = roles[self['role']]

    async def etag(self):
        return self.request.app['etag']

    @property
    def link_title(self):
        return self._role['name']

    async def attributes(self):
        result = await super().attributes()
        if 'description' in self._role:
            result['description'] = publish_parts(self._role['description'], writer_name='html')['fragment']
        return result

    async def _links(self):
        return {
            'profile': [
                _profiles.Profile(
                    self.request,
                    {'profile': profile},
                    self.embed.get('profile')
                ) for profile in self._role['profiles']
            ],
            'account': [
                _accounts.Account(
                    self.request,
                    {'account': account_name},
                    self.embed.get('account')
                ) async for account_name in database.account_names_with_role(self.request, self['role'])
            ]
        }
