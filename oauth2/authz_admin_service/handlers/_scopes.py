import logging

from aiohttp import web

from oauth2 import view
from . import _datasets

_logger = logging.getLogger(__name__)


class Scopes(view.OAuth2View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        datasets = self.request.app['config']['authz_admin_service']['datasets']
        if self['dataset'] not in datasets:
            raise web.HTTPNotFound
        self._dataset = datasets[self['dataset']]

    @property
    def etag(self):
        return self.request.app['etag']

    @property
    def name(self):
        return '%s.scopes' % self['dataset']

    @property
    def title(self):
        return "Scopes in dataset %s" % self._dataset['name']

    async def all_links(self):
        items = [
            Scope(
                self.request,
                {'dataset': self['dataset'], 'scope': name},
                self.embed.get('item')
            )
            for name in self._dataset['scopes']
        ]
        return {'item': items}


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
    def name(self):
        return "%s.%s" % (
            self['dataset'],
            self['scope'],
        )

    @property
    def title(self):
        return "%s (for dataset %s)" % (
            self._scope['name'],
            self._dataset['name']
        )

    @property
    def etag(self):
        return self.request.app['etag']

    async def all_links(self):
        result = {
            'dataset': _datasets.Dataset(self.request, self.match_dict, embed=self.embed.get('dataset'))
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
        result = await super().attributes()
        if 'description' in self._scope:
            result['description'] = self._scope['description']
        return result
