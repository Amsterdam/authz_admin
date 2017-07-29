import logging

from aiohttp import web

from rest_utils import resources
from .dataset import Dataset

_logger = logging.getLogger(__name__)


class Datasets(resources.PlainResource):

    @property
    def name(self):
        return 'Datasets'

    async def all_links(self, request: web.Request):
        items = []
        embed = self.embed.get('item')
        query = {} if embed is None else {'embed': embed}
        for name in request.app['config']['datasets']:
            items.append(
                Dataset(
                    request,
                    web.URL(self.rel_url.raw_path + name).update_query(query)
                )
            )
        return {'item': items}
