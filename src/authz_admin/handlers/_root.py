import logging

from authz_admin import view
from . import _accounts, _scopes, _roles, _profiles

_logger = logging.getLogger(__name__)


class Root(view.OAuth2View):

    async def etag(self):
        return True

    @property
    def link_title(self):
        return 'Authorization Administration API'

    async def _links(self):
        accounts = _accounts.Accounts(
            self.request,
            {},
            embed=self.embed.get('accounts')
        )
        datasets = _scopes.Datasets(
            self.request,
            {},
            embed=self.embed.get('datasets')
        )
        profiles = _profiles.Profiles(
            self.request,
            {},
            embed=self.embed.get('profiles')
        )
        roles = _roles.Roles(
            self.request,
            {},
            embed=self.embed.get('roles')
        )
        return {
            'accounts': accounts,
            'datasets': datasets,
            'profiles': profiles,
            'roles': roles
        }
