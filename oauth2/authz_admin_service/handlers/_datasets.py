import logging

from aiohttp import web

from oauth2 import view
from . import _scopes

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
        scopes = _scopes.Scopes(
            self.request,
            self.match_dict,
            embed=self.embed.get('scopes')
        )
        result = {'scopes': scopes}
        if 'describedby' in self._dataset:
            result['describedby'] = {'href': self._dataset['describedby']}
        return result
