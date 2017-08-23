import logging

from aiohttp import web

from oauth2 import view
from . import _idps

_logger = logging.getLogger(__name__)


class Users(view.OAuth2View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # TODO: implement

    @property
    def etag(self):
        # TODO: implement
        return None

    @property
    def link_title(self):
        return "Users in IdP %s" % self['idp']

    async def all_links(self):
        items = [
            User(
                self.request,
                {'idp': self['idp'], 'user': name},
                self.embed.get('item')
            )
            for name in self._idp['users']
        ]
        return {
            'item': items,
            'up': _idps.IdP(self.request, self.match_dict, self.embed.get('up'))
        }


class User(view.OAuth2View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        idps = self.request.app['config']['idps']
        if self['idp'] not in idps:
            raise web.HTTPNotFound(text="No such idp")
        self._idp = idps[self['idp']]
        users = self._idp['users']
        if self['user'] not in users:
            raise web.HTTPNotFound(text="No such user")
        self._user = users[self['user']]

    @property
    def link_name(self):
        return "%s.%s" % (
            self['idp'],
            self['user'],
        )

    @property
    def link_title(self):
        return "%s (for idp %s)" % (
            self._user['name'],
            self._idp['name']
        )

    @property
    def etag(self):
        return self.request.app['etag']

    async def all_links(self):
        result = {
            'idp': _idps.IdP(self.request, self.match_dict, embed=self.embed.get('idp')),
            'up': Users(self.request, self.match_dict, self.embed.get('up'))
        }
        for fieldname in ('includes', 'included_by'):
            if fieldname in self._user:
                result[fieldname] = User(
                    self.request,
                    {'idp': self['idp'], 'user': self._user[fieldname]},
                    embed=self.embed.get(fieldname)
                )
        return result

    async def attributes(self):
        result = await super().attributes()
        if 'description' in self._user:
            result['description'] = self._user['description']
        return result
