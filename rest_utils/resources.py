import abc
import inspect
import logging
import re
from typing import Dict, Union, List, Tuple, Optional, Type, Any

import collections.abc
from aiohttp import web
from multidict import MultiDict

from types import MappingProxyType
from .best_content_type import best_content_type
from .default_query_params import default_query_params
from .json import encode as async_encode
from .parse_embed import parse_embed

_logger = logging.getLogger(__name__)


def _slashify(s):
    assert isinstance(s, str)
    return s if s.endswith('/') else s + '/'

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


class Resource(metaclass=abc.ABCMeta):

    SEGMENT_RE = re.compile(r'([^/{}]+)/?$')

    PATHS = {}
    PATTERNS = {}

    _HANDLER_NAMES = {
        'delete_handler': ('DELETE', None),
        'get_handler': ('GET', None),
        'head_handler': ('HEAD', None),
        'options_handler': ('OPTIONS', None),
        'patch_handler': ('PATCH', 'patch_expect_handler'),
        'post_handler': ('POST', 'post_expect_handler'),
        'put_handler': ('PUT', 'put_expect_handler')
    }

    def __init__(self, request: web.Request, rel_url: web.URL):
        self.__rel_url = rel_url
        self.__dqps = default_query_params(request, rel_url.raw_path)
        self.__embed = None
        self.__query = None
        self.__canonical_rel_url = None

    @property
    def rel_url(self) -> web.URL:
        # language=rst
        """The relative URL as passed to the constructor."""
        return self.__rel_url

    @property
    def canonical_rel_url(self) -> web.URL:
        # language=rst
        """Like :meth:`rel_url`, but without query parameters that have default values."""
        if self.__canonical_rel_url is None:
            query = MultiDict(self.__rel_url.query)
            # _logger.debug("query: %s", query)
            for key, value in self.__dqps.items():
                if key in query and query.getall(key) == [value]:
                    del query[key]
            self.__canonical_rel_url = self.__rel_url.with_query(query)
            # _logger.debug("self.__canonical_rel_url: %s", self.__canonical_rel_url)
        # noinspection PyTypeChecker
        return self.__canonical_rel_url

    @property
    def to_link(self):
        return {
            'href': str(self.canonical_rel_url),
            'name': self.name,
            'type': "application/hal+json; charset=UTF-8"
        }

    @property
    def query(self):
        # language=rst
        """Like ``self.rel_url.query``, but with default parameters added.

        These default parameters are retrieved from the swagger definition.

        """
        if self.__query is None:
            self.__query = MultiDict(self.__dqps)
            self.__query.update(self.__rel_url.query)
        return self.__query

    @property
    def embed(self):
        if self.__embed is None:
            embed = ','.join(self.query.getall('embed', default=[]))
            self.__embed = parse_embed(embed)
        return self.__embed

    @staticmethod
    def construct_resource_for(request: web.Request, raw_path: str, embed=None):
        """

        :rtype: Resource | None

        """
        rel_url = web.URL(raw_path)
        if embed is not None:
            rel_url = rel_url.with_query(embed=embed)
        embed = {} if embed is None else {'embed': embed}
        for resource in request.app.router.resources():
            match_dict = resource._match(raw_path)
            if match_dict is not None:
                if hasattr(resource, 'rest_utils_class'):
                    return resource.rest_utils_class(request, rel_url)
                _logger.warning("Path %s doesn't resolve to rest_utils resource.", raw_path)
                return None
        return None

    @classmethod
    def add_to_router(cls, router, path):
        # language=rst
        """

        :param aiohttp.web.UrlDispatcher router:
        :param str path:
        :param str name:

        """
        cls._resource = router.add_resource(path)
        # Register the current class in the appropriate registry:
        if isinstance(cls._resource, web.DynamicResource):
            Resource.PATTERNS[cls._resource.get_info()['pattern']] = cls
        elif isinstance(cls._resource, web.PlainResource):
            Resource.PATHS[cls._resource.get_info()['path']] = cls
        else:
            _logger.critical("aiohttp router method 'add_resource()' returned resource object of unexpected type %s", cls._resource.__class__)
        cls._resource.rest_utils_class = cls
        for handler_name, (method, expect_handler_name) in cls._HANDLER_NAMES.items():
            handler = getattr(cls, handler_name, None)
            # Assert method exists and is a @classmethod:
            if handler and inspect.ismethod(handler):
                expect_handler = expect_handler_name and \
                                 getattr(cls, expect_handler_name, None)
                if expect_handler:
                    assert inspect.ismethod(expect_handler)
                    cls._resource.add_route(method, handler, expect_handler=expect_handler)
                else:
                    cls._resource.add_route(method, handler)
        return cls._resource

    @classmethod
    def resource(cls) -> web.Resource:
        assert hasattr(cls, '_resource'), \
            "%s.resource() called before .add_to_router()" % cls
        return cls._resource

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    async def attributes(self, request: web.Request):
        # language=rst
        """

        This default implementation returns *no* attributes, ie. an empty
        `dict`.

        Most stubclasses should override this default implementation.

        """
        return {}

    @abc.abstractmethod
    async def all_links(self, request: web.Request) -> Dict[str, Any]:
        # language=rst
        """

        Called by :meth:`Resource.links` and :meth:`Resource.embedded`.  See the
        documentation of these methods for more info.

        This default implementation returns "subresources" of ``self``
        found in the router.

        Some subclasses may want to override this method.

        :returns: This method must return a dict.  The values must have one of
            the following types:

            - asynchronous generator of `Resource` objects
            - generator of `Resource` objects
            - `Resource`
            - link
            - Iterable of `Resource` and/or link objects (may be mixed)

            where *link* is a HALJSON link object, ie. a `dict` with at least a
            key ``href``.

        """
        pass

    async def embedded(self, request: web.Request) -> Dict[str, Any]:
        result = {}
        all_links = await self.all_links(request)
        for key, value in all_links.items():
            if key in self.embed:
                if inspect.isasyncgen(value):
                    async def g1():
                        async for resource in value:
                            yield await resource.to_dict(request)
                    result[key] = g1()
                elif inspect.isgenerator(value):
                    async def g2():
                        for resource in value:
                            yield await resource.to_dict(request)
                    result[key] = g2()
                elif isinstance(value, Resource):
                    result[key] = await value.to_dict(request)
                elif isinstance(value, collections.abc.Iterable):
                    async def g3():
                        for resource in value:
                            if isinstance(resource, Resource):
                                yield await resource.to_dict(request)
                    result[key] = g3()
                else:
                    _logger.error("Don't know how to embed object: %s", value)
        return result

    async def links(self, request: web.Request) -> Dict[str, Any]:
        result = {}
        all_links = await self.all_links(request)
        for key, value in all_links.items():
            if key not in self.embed and inspect.isasyncgen(value):
                async def g1(resources):
                    async for resource in resources:
                        yield resource.to_link
                result[key] = g1(value)
            elif key not in self.embed and inspect.isgenerator(value):
                def g2(resources):
                    for resource in resources:
                        yield resource.to_link
                result[key] = g2(value)
            elif key not in self.embed and isinstance(value, Resource):
                result[key] = value.to_link
            elif isinstance(value, collections.Mapping):
                if key in self.embed:
                    _logger.info('Client asked to embed unembeddable object: %s', value)
                result[key] = value
            elif isinstance(value, collections.abc.Iterable):
                def g3():
                    for o in value:
                        if not isinstance(o, Resource):
                            yield o
                        elif key not in self.embed:
                            yield o.to_link
                result[key] = g3()
            elif key not in self.embed:
                _logger.error("Don't know how to render object as link: %s", value)
        return result

    @classmethod
    async def get_handler(cls, request: web.Request):
        # language=rst
        """

        :param aiohttp.web.Request request:
        :rtype: aiohttp.web.Response

        """
        response = web.StreamResponse()
        response.content_type = best_content_type(request)
        response.enable_compression()
        resource = cls(request, request.rel_url)
        data = await resource.to_dict(request)
        await response.prepare(request)
        async for chunk in async_encode(data):
            response.write(chunk)
            await response.drain()
        response.write_eof()
        return response

    async def to_dict(self, request: web.Request):
        result = await self.attributes(request)
        if 'name' not in result:
            result['name'] = self.name
        result['_links'] = await self.links(request)
        if 'self' not in result['_links']:
            result['_links']['self'] = self.to_link
        result['_embedded'] = await self.embedded(request)
        if len(result['_embedded']) == 0:
            del result['_embedded']
        return result


class DynamicResource(Resource, metaclass=abc.ABCMeta):

    def __init__(self, request: web.Request, rel_url: web.URL):
        super().__init__(request, rel_url)
        self.__match_dict = MappingProxyType(
            # Ugly: we're using non-public member ``match()`` of
            # :class:`aiohttp.web.DynamicResource`
            self.__class__._resource._match(rel_url.raw_path)
        )

    @property
    def match_dict(self):
        return self.__match_dict

    async def all_links(self, request: web.Request) -> Dict[str, Any]:
        # language=rst
        """Overrides :meth:`Resource.all_links`.

        This default implementation returns "subresources" of ``self``
        found in the router.

        Some subclasses may want to override this method.

        """
        result = {}
        # noinspection PyUnresolvedReferences
        formatter = _slashify(self.resource().get_info()['formatter'])
        for aiohttp_resource in request.app.router.resources():
            if not isinstance(aiohttp_resource, web.DynamicResource):
                continue
            sub_formatter = aiohttp_resource.get_info()['formatter']
            if not sub_formatter.startswith(formatter):
                continue
            match = self.SEGMENT_RE.match(sub_formatter, len(formatter))
            if match is None:
                continue
            sub_raw_path = _slashify(self.rel_url.raw_path) + match[0]
            sub_resource = self.construct_resource_for(
                request, sub_raw_path, self.embed.get(match[0])
            )
            result[match[1]] = sub_resource if sub_resource else {
                'href': sub_raw_path,
                'name': match[1]
            }
        return result


class PlainResource(Resource, metaclass=abc.ABCMeta):

    async def all_links(self, request: web.Request):
        # language=rst
        """Overrides :meth:`Resource.all_links`.

        This default implementation returns "subresources" of ``self``
        found in the router.

        Some subclasses may want to override this method.

        """
        result = {}
        # noinspection PyUnresolvedReferences
        path = _slashify(self.resource().get_info()['path'])
        for aiohttp_resource in request.app.router.resources():
            if not isinstance(aiohttp_resource, web.PlainResource):
                continue
            sub_path = aiohttp_resource.get_info()['path']
            if not sub_path.startswith(path):
                continue
            match = self.SEGMENT_RE.match(sub_path, len(path))
            if match is None:
                continue
            sub_raw_path = _slashify(self.rel_url.raw_path) + match[0]
            sub_resource = self.construct_resource_for(
                request, sub_raw_path, self.embed.get(match[0])
            )
            result[match[1]] = sub_resource if sub_resource else {
                'href': str(sub_raw_path),
                'name': match[1]
            }
        return result
