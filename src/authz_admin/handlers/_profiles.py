import logging
from docutils.core import publish_parts

from aiohttp import web

from authz_admin import view
from . import _roles, _scopes

_logger = logging.getLogger(__name__)


class Profiles(view.OAuth2View):

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # TODO: implement

    async def etag(self):
        return self.request.app['etag']

    @property
    def link_title(self):
        return "Profiles"

    async def _links(self):
        items = [
            Profile(
                self.request,
                {'profile': name},
                self.embed.get('item')
            )
            for name in self.request.app['config']['authz_admin']['profiles']
        ]
        return {'item': items}


class Profile(view.OAuth2View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profiles = self.request.app['config']['authz_admin']['profiles']
        if self['profile'] not in profiles:
            raise web.HTTPNotFound()
        self._profile = profiles[self['profile']]

    async def etag(self):
        return self.request.app['etag']

    @property
    def link_title(self):
        return self._profile['name']

    async def attributes(self):
        result = await super().attributes()
        if 'description' in self._profile:
            result['description'] = publish_parts(self._profile['description'], writer_name='html')['fragment']
        return result

    async def _links(self):
        result = {
            'scope': [],
            'role': [
                _roles.Role(
                    self.request,
                    {'role': role_name},
                    self.embed.get('role')
                ) for role_name, role
                in self.request.app['config']['authz_admin']['roles'].items()
                if self['profile'] in role['profiles']
            ]}
        for scope_name in self._profile['scopes']:
            dataset_name, scope_name = scope_name.split('/', 2)
            result['scope'].append(
                _scopes.Scope(
                    self.request,
                    {'dataset': dataset_name, 'scope': scope_name},
                    self.embed.get('scope')
                )
            )
        return result
