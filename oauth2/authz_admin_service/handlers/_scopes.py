import logging

from aiohttp import web

from oauth2 import view
from . import _profiles

_logger = logging.getLogger(__name__)


class Datasets(view.OAuth2View):

    @property
    def etag(self):
        return self.request.app['etag']

    @property
    def link_title(self):
        return 'Datasets'

    async def _links(self):
        items = [
            Dataset(
                self.request,
                {'dataset': name},
                self.embed.get('item')
            )
            for name in self.request.app['config']['authz_admin_service']['datasets']
        ]
        return {'item': items}


class Dataset(view.OAuth2View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        datasets = self.request.app['config']['authz_admin_service']['datasets']
        if self['dataset'] not in datasets:
            raise web.HTTPNotFound()
        self._dataset = datasets[self['dataset']]

    @property
    def link_title(self):
        return self._dataset['name']

    @property
    def etag(self):
        return self.request.app['etag']

    async def _links(self):
        result = {
            'item': [
                Scope(
                    self.request,
                    {'dataset': self['dataset'], 'scope': name},
                    self.embed.get('item')
                )
                for name in self._dataset['scopes']
            ]
        }
        if 'described_by' in self._dataset:
            result['described_by'] = {'href': self._dataset['described_by']}
        return result


class Scope(view.OAuth2View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        datasets = self.request.app['config']['authz_admin_service']['datasets']
        if self['dataset'] not in datasets:
            raise web.HTTPNotFound(text="No such dataset")
        self._dataset = datasets[self['dataset']]
        scopes = self._dataset['scopes']
        if self['scope'] not in scopes:
            raise web.HTTPNotFound(text="No such scope")
        self._scope = scopes[self['scope']]

    @property
    def link_name(self):
        return "%s/%s" % (
            self['dataset'],
            self['scope'],
        )

    @property
    def link_title(self):
        return "%s (for dataset '%s')" % (
            self._scope['name'],
            self['dataset']
        )

    @property
    def etag(self):
        return self.request.app['etag']

    async def _links(self):
        result = {
            'profile': [
                _profiles.Profile(
                    self.request,
                    {'profile': profile_name},
                    self.embed.get('profile')
                ) for profile_name, profile
                in self.request.app['config']['authz_admin_service']['profiles'].items()
                if self['scope'] in profile['scopes']
            ]
        }
        for fieldname in ('includes', 'included_by'):
            if fieldname in self._scope:
                result[fieldname] = Scope(
                    self.request,
                    {'dataset': self['dataset'], 'scope': self._scope[fieldname]},
                    embed=self.embed.get(fieldname)
                )
        return result

    async def attributes(self):
        result = {'name': self._scope['name']}
        if 'description' in self._scope:
            result['description'] = self._scope['description']
        return result
