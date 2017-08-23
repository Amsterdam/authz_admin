import logging

from aiohttp import web

from oauth2 import view
from . import _users, _root

_logger = logging.getLogger(__name__)


class IdPs(view.OAuth2View):

    @property
    def etag(self):
        return self.request.app['etag']

    @property
    def title(self):
        return 'IdPs'

    async def _links(self):
        # TODO: implement
        items = []
        return {
            'item': items,
            'up': _root.Root(self.request, {}, self.embed.get('up'))
        }


class IdP(view.OAuth2View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        idps = self.request.app['config']['idps']
        if self['idp'] not in idps:
            raise web.HTTPNotFound
        self._idp = idps[self['idp']]

    @property
    def title(self):
        return self._idp['name']

    @property
    def etag(self):
        return self.request.app['etag']

    async def _links(self):
        users = _users.Users(self.request, self.match_dict, embed=self.embed.get('users'))
        result = {
            'up': IdPs(self.request, {}, embed=self.embed.get('up')),
            'users': users
        }
        if 'describedby' in self._idp:
            result['describedby'] = {'href': self._idp['describedby']}
        return result
