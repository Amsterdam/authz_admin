import logging
import re

from aiohttp import web

from oauth2 import view
from . import _roles, _scopes

_logger = logging.getLogger(__name__)


class Profiles(view.OAuth2View):

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # TODO: implement

    @property
    def etag(self):
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
            for name in self.request.app['config']['authz_admin_service']['profiles']
        ]
        return {'item': items}


class Profile(view.OAuth2View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profiles = self.request.app['config']['authz_admin_service']['profiles']
        if self['profile'] not in profiles:
            raise web.HTTPNotFound()
        self._profile = profiles[self['profile']]

    @property
    def etag(self):
        return self.request.app['etag']

    @property
    def link_title(self):
        return self._profile['name']

    async def attributes(self):
        result = await super().attributes()
        if 'description' in self._profile:
            result['description'] = self._profile['description']
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
                in self.request.app['config']['authz_admin_service']['roles'].items()
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
