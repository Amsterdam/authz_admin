import abc
import re

from aiohttp import web

from .aiohttp_utils import best_content_type
from .json import encode as async_encode


# class AbstractResource(metaclass=abc.ABCMeta):
#
#     @abc.abstractmethod
#     async def attributes(self, request):
#         # language=rst
#         """
#
#         :param aiohttp.web.Request request:
#
#         """
#         return {}
#
#     @abc.abstractmethod
#     async def links(self, request):
#         # language=rst
#         """
#
#         :param aiohttp.web.Request request:
#
#         """
#         return {}
#
#     @abc.abstractmethod
#     async def embedded(self, request):
#         # language=rst
#         """
#
#         :param aiohttp.web.Request request:
#
#         """
#         return {}
#
#     @property
#     @abc.abstractmethod
#     def aiohttp_resource(self) -> web.Resource:
#         pass


# noinspection PyMethodMayBeStatic,PyUnusedLocal
class Resource:

    def __init__(self, aiohttp_resource, name_formatter=None):
        # language=rst
        """

        :param aiohttp.web.Resource aiohttp_resource:
        :param str name_formatter:

        """
        if isinstance(aiohttp_resource, web.DynamicResource):
            assert name_formatter is not None
        assert aiohttp_resource.name
        super().__init__()
        self._aiohttp_resource = aiohttp_resource
        self._name_formatter = name_formatter
        aiohttp_resource.rest_utils_resource = self
        aiohttp_resource.add_route('GET', self.get_handler)

    def name_for(self, match_info):
        return self._name_formatter.format_map(match_info) \
            if self._name_formatter else self.aiohttp_resource.name

    async def attributes(self, request):
        # language=rst
        """

        :param aiohttp.web.Request request:

        """
        return {}

    async def links(self, request):
        # language=rst
        """

        :param aiohttp.web.Request request:

        """
        return {}

    SUB_RE = re.compile('([^/]+)(/?)$')

    async def embedded(self, request):
        # language=rst
        """

        :param aiohttp.web.Request request:

        """
        return {}

    @property
    def aiohttp_resource(self) -> web.Resource:
        return self._aiohttp_resource

    async def get_handler(self, request):
        response = web.StreamResponse()

        response.content_type = best_content_type(request)

        await response.prepare(request)
        async for chunk in async_encode(await self.to_dict(request)):
            response.write(chunk)
            await response.drain()
        response.write_eof()
        return response

    async def to_dict(self, request):
        # language=rst
        """

        :param aiohttp.web.Request request:

        """
        result = await self.attributes(request)
        result['_links'] = await self.links(request)
        if 'self' not in result['_links']:
            result['_links']['self'] = {
                'href': str(request.rel_url),
                'name': self.name_for(request.match_info)
            }
        return result


class DumbCollection(Resource):

    def _plain_resource_items(self, request):
        self_path = self.aiohttp_resource.get_info()['path']
        pattern = re.compile(re.escape(self_path) + '([^{/]+)(/?)$')
        for resource in request.app.router.resources():
            if not isinstance(resource, web.PlainResource):
                continue
            match = pattern.match(resource.get_info()['path'])
            if match:
                yield {
                    'href': match[0],
                    'name': (resource.name or match[1])
                }

    def _dynamic_resource_items(self, request):
        self_formatter = self.aiohttp_resource.get_info()['formatter']
        pattern = re.compile(re.escape(self_formatter) + '([^{/]+)(/?)$')
        for resource in request.app.router.resources():
            if not isinstance(resource, web.DynamicResource):
                continue
            match = pattern.match(resource.get_info()['formatter'])
            if match:
                yield {
                    'href': match[0],
                    'name': resource.rest_utils_resource.name_for(request.match_info)
                }

    async def links(self, request):
        """The default implementation of :func:`AbstractResource.links`.

        Returns sub-resources found in the application's router.

        :param aiohttp.web.Request request:

        """
        assert request.raw_path.endswith('/')
        items = self._plain_resource_items(request) \
            if isinstance(self.aiohttp_resource, web.PlainResource) \
            else self._dynamic_resource_items(request)
        items = list(items)
        if len(items) == 0:
            return {}
        return {'items': items}
