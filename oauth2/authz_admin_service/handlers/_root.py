import logging

from oauth2 import view
from ._accounts import Accounts
from ._datasets import Datasets
from ._roles import Roles

_logger = logging.getLogger(__name__)


class Root(view.OAuth2View):

    @property
    def etag(self):
        return self.request.app['etag']

    @property
    def link_title(self):
        return 'Authorization Administration API'

    async def _links(self):
        accounts = Accounts(
            self.request,
            self.match_dict,
            embed=self.embed.get('accounts')
        )
        datasets = Datasets(
            self.request,
            self.match_dict,
            embed=self.embed.get('datasets')
        )
        roles = Roles(
            self.request,
            self.match_dict,
            embed=self.embed.get('roles')
        )
        return {
            'datasets': datasets
        }

    # _INSTANCE = None
    #
    # @classmethod
    # def instance_for_request(cls, request: web.Request):
    #     if cls._INSTANCE is None:
    #         cls._INSTANCE = Root()
    #     return cls._INSTANCE
