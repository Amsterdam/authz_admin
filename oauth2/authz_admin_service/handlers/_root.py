import logging

from oauth2 import view
from . import _datasets

_logger = logging.getLogger(__name__)


class Root(view.OAuth2View):

    @property
    def etag(self):
        return self.request.app['etag']

    @property
    def title(self):
        return 'Authorization Administration API'

    async def all_links(self):
        datasets = _datasets.Datasets(
            self.request,
            self.match_dict,
            embed=self.embed.get('datasets')
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
