from aiohttp import web

from rest_utils import resources


class Dataset(resources.DynamicResource):

    def __init__(self, request: web.Request, rel_url: web.URL):
        super().__init__(request, rel_url)
        self._data = request.app['config']['datasets'][self.match_dict['dataset']]

    @property
    def name(self):
        return self._data['name']

    async def all_links(self, request: web.Request):
        result = {}
        if 'describedby' in self._data:
            result['describedby'] = {'href': self._data['describedby']}
        return result
