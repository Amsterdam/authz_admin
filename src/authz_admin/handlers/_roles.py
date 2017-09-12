import logging

from aiohttp import web
from docutils.core import publish_parts

from authz_admin import database
from authz_admin import view
from . import _profiles, _accounts

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
            for name in self.request.app['config']['authz_admin']['roles']
        ]
        return {'item': items}


class Role(view.OAuth2View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        roles = self.request.app['config']['authz_admin']['roles']
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
                    {'account': row['account_id']},
                    self.embed.get('account'),
                    data=dict(row)
                ) async for row in database.accounts(self.request, [self['role']])
            ]
        }
