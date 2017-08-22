import logging

from aiohttp import web

from oauth2 import view
from . import _idps

_logger = logging.getLogger(__name__)


class Roles(view.OAuth2View):

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # TODO: implement

    @property
    def etag(self):
        return self.request.app['etag']

    @property
    def link_title(self):
        return "ADW Rollen"

    async def all_links(self):
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

    @property
    def etag(self):
        return self.request.app['etag']

    @property
    def link_title(self):
        return self._role['name']

    async def attributes(self):
        result = await super().attributes()
        if 'description' in self._role:
            result['description'] = self._role['description']
        return result
