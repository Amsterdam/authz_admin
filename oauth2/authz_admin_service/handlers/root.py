import logging

from aiohttp import web

from rest_utils import resources

_logger = logging.getLogger(__name__)


class Root(resources.PlainResource):
    @property
    def name(self):
        return 'Root'

    # _INSTANCE = None
    #
    # @classmethod
    # def instance_for_request(cls, request: web.Request):
    #     if cls._INSTANCE is None:
    #         cls._INSTANCE = Root()
    #     return cls._INSTANCE

    async def attributes(self, request: web.Request):
        _, path_info = request.app['rest_utils.swagger'].get_path_spec(request.rel_url.raw_path, 'get')
        return {'swagger_stuff': path_info}
