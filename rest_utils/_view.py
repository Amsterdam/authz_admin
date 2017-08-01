import collections.abc
import inspect
import logging
import re
import typing as T

from aiohttp import web
from multidict import MultiDict

from . import _json
from ._middleware import BEST_CONTENT_TYPE, ASSERT_PRECONDITIONS
from ._parse_embed import parse_embed

_logger = logging.getLogger(__name__)


def _slashify(s):
    assert isinstance(s, str)
    return s if s.endswith('/') else s + '/'


class View(web.View):

    SEGMENT_RE = re.compile(r'([^/{}]+)/?$')
    PATHS = {}
    PATTERNS = {}

    def __init__(
            self, request: web.Request,
            rel_url: T.Union[web.URL, collections.abc.Mapping]=None,
            embed=None
    ):
        super().__init__(request)
        if rel_url is None:
            rel_url = request.rel_url
        elif not isinstance(rel_url, web.URL):
            assert isinstance(rel_url, collections.abc.Mapping)
            rel_url = self.resource().url_for(**rel_url)
        if embed is not None:
            rel_url = rel_url.update_query(embed=embed)
        self.__rel_url = rel_url
        self.__embed = None
        self.__query = None
        self.__canonical_rel_url = None
        self.__etag = None
        self.__match_dict = dict(
            # Ugly: we're using non-public member ``_match()`` of
            # :class:`aiohttp.web.Resource`.  But most alternatives are
            # equally ugly.
            self.resource()._match(self.rel_url.raw_path)
        )

    def __getitem__(self, item):
        """Shorthand for ``self.match_dict[item]``"""
        return self.__match_dict[item]

    @property
    def match_dict(self):
        return self.__match_dict

    def add_embed_to_url(self, url: web.URL, link_relation):
        embed = self.embed.get(link_relation)
        if embed is None:
            return url
        return url.update_query(embed=embed)

    @property
    def rel_url(self) -> web.URL:
        # language=rst
        """The relative URL as passed to the constructor."""
        return self.__rel_url

    @property
    def canonical_rel_url(self) -> web.URL:
        # language=rst
        """Like :meth:`rel_url`, but with all default query parameters explicitly listed."""
        if self.__canonical_rel_url is None:
            self.__canonical_rel_url = self.__rel_url.with_query(self.query)
        # noinspection PyTypeChecker
        return self.__canonical_rel_url

    @property
    def to_link(self) -> T.Dict[str, str]:
        """The HAL JSON link object to this resource."""
        return {
            'href': str(self.canonical_rel_url),
            'name': self.name
        }

    @property
    def etag(self) -> T.Union[None, bool, str]:
        # language=rst
        """

        Return values have the following meanings:

        ``True``
            Resource exists and doesn have an ETag.
        ``False``
            Resource doesn't exist.
        ``None``
            Resource may or may not exist and doesn't support ETags.
        ETag string:
            Resource exists and supports ETags.

        """
        return None

    @property
    def query(self):
        # language=rst
        """Like ``self.rel_url.query``, but with default parameters added.

        These default parameters are retrieved from the swagger definition.

        """
        if self.__query is None:
            self.__query = MultiDict(self.default_query_params)
            self.__query.update(self.__rel_url.query)
        return self.__query

    @property
    def embed(self):
        if self.__embed is None:
            embed = ','.join(self.query.getall('embed', default=[]))
            self.__embed = parse_embed(embed)
        return self.__embed

    @staticmethod
    def construct_resource_for(request: web.Request, rel_url: web.URL) \
            -> T.Optional[web.View]:
        """

        .. deprecated::

            Only used by :meth:`PlainView.all_links` and
            :meth:`DynamicView.all_links`, which are themselves deprecated.

        """
        for resource in request.app.router.resources():
            match_dict = resource._match(rel_url.raw_path)
            if match_dict is not None:
                if hasattr(resource, 'rest_utils_class'):
                    return resource.rest_utils_class(request, rel_url)
                _logger.error("Path %s doesn't resolve to rest_utils.Resource.", str(rel_url))
                return None
        return None

    @property
    def default_query_params(self) -> T.Dict[str, str]:
        return {}

    @classmethod
    def add_to_router(cls, router, path, expect_handler=None):
        # language=rst
        """

        :param aiohttp.web.UrlDispatcher router:
        :param str path:
        :param str name:

        """
        cls._resource = router.add_resource(path)
        # Register the current class in the appropriate registry:
        if isinstance(cls._resource, web.DynamicResource):
            View.PATTERNS[cls._resource.get_info()['pattern']] = cls
        elif isinstance(cls._resource, web.PlainResource):
            View.PATHS[cls._resource.get_info()['path']] = cls
        else:
            _logger.critical("aiohttp router method 'add_resource()' returned resource object of unexpected type %s", cls._resource.__class__)
        cls._resource.rest_utils_class = cls
        cls._resource.add_route('*', cls, expect_handler=expect_handler)
        return cls._resource

    @classmethod
    def resource(cls) -> T.Union[web.PlainResource, web.DynamicResource]:
        assert hasattr(cls, '_resource'), \
            "%s.resource() called before .add_to_router()" % cls
        return cls._resource

    @property
    def name(self) -> str:
        return self.rel_url.name or self.rel_url.parent.name

    async def attributes(self):
        # language=rst
        """

        This default implementation returns *no* attributes, ie. an empty
        `dict`.

        Most stubclasses should override this default implementation.

        """
        return {}

    async def all_links(self) -> T.Dict[str, T.Any]:
        # language=rst
        """

        Called by :meth:`Resource.links` and :meth:`Resource.embedded`.  See the
        documentation of these methods for more info.

        :returns: This method must return a dict.  The values must have one of
            the following types:

            -   asynchronous generator of `Resource` objects
            -   generator of `Resource` objects
            -   `Resource`
            -   link
            -   Iterable of `Resource` and/or link objects (may be mixed)

            where *link* is a HALJSON link object, ie. a `dict` with at least a
            key ``href``.

        """
        return {}

    async def embedded(self) -> T.Dict[str, T.Any]:
        result = {}
        all_links = await self.all_links()
        for key, value in all_links.items():
            if key in self.embed:
                if (inspect.isasyncgen(value) or
                    inspect.isgenerator(value) or
                    isinstance(value, View) or
                    isinstance(value, collections.abc.Iterable)
                ):
                    result[key] = value
                else:
                    _logger.error("Don't know how to embed object: %s", value)
        return result

    async def links(self) -> T.Dict[str, T.Any]:
        result = {}
        all_links = await self.all_links()
        for key, value in all_links.items():
            if key == 'item':
                key = 'item'
            if isinstance(value, View):
                if key not in self.embed:
                    result[key] = value.to_link
            elif inspect.isasyncgen(value):
                if key not in self.embed:
                    async def g1(resources):
                        async for resource in resources:
                            yield resource.to_link
                    result[key] = g1(value)
            elif inspect.isgenerator(value):
                if key not in self.embed:
                    def g2(resources):
                        for resource in resources:
                            yield resource.to_link
                    result[key] = g2(value)
            elif isinstance(value, collections.Mapping):
                if key in self.embed:
                    _logger.info('Client asked to embed unembeddable object: %s', value)
                result[key] = value
            elif isinstance(value, collections.abc.Iterable):
                def g3(key, value):
                    for o in value:
                        if not isinstance(o, View):
                            if key in self.embed:
                                _logger.info('Client asked to embed unembeddable object: %s', o)
                            yield o
                        elif key not in self.embed:
                            yield o.to_link
                result[key] = g3(key, value)
            elif key not in self.embed:
                _logger.error("Don't know how to render object as link: %s", value)
        return result

    async def get(self) -> web.StreamResponse:
        assert 'GET_IN_PROGRESS' not in self.request
        self.request['GET_IN_PROGRESS'] = True
        self.request[ASSERT_PRECONDITIONS](self.etag)
        data = await self.to_dict()
        response = web.StreamResponse()
        if isinstance(self.etag, str):
            response.headers.add('ETag', self.etag)
        response.content_type = self.request[BEST_CONTENT_TYPE]
        response.enable_compression()
        await response.prepare(self.request)
        async for chunk in _json.json_encode(data):
            response.write(chunk)
        response.write_eof()
        return response

    async def to_dict(self):
        result = await self.attributes()
        if isinstance(self.etag, str):
            result['_etag'] = self.etag
        result['_links'] = await self.links()
        if 'self' not in result['_links']:
            result['_links']['self'] = self.to_link
        result['_embedded'] = await self.embedded()
        if len(result['_embedded']) == 0:
            del result['_embedded']
        return result


class DynamicView(View):
    """

    .. deprecated::

        Functionality of classes :class:`DynamicView` and :class:`PlainView` was
        moved into :class:`View`. This class is here only to keep method
        :meth:`all_links` around.

    """

    async def all_links(self) -> T.Dict[str, T.Any]:
        # language=rst
        """Overrides :meth:`Resource.all_links`.

        This default implementation returns "subresources" of ``self``
        found in the router.

        Some subclasses may want to override this method.

        """
        result = {}
        # noinspection PyUnresolvedReferences
        formatter = _slashify(self.resource().get_info()['formatter'])
        for aiohttp_resource in self.request.app.router.resources():
            if not isinstance(aiohttp_resource, web.DynamicResource):
                continue
            sub_formatter = aiohttp_resource.get_info()['formatter']
            if not sub_formatter.startswith(formatter):
                continue
            match = self.SEGMENT_RE.match(sub_formatter, len(formatter))
            if match is None:
                continue
            sub_rel_url = web.URL(_slashify(self.rel_url.raw_path) + match[0])
            sub_rel_url = self.add_embed_to_url(sub_rel_url, match[0])
            sub_resource = self.construct_resource_for(
                self.request, sub_rel_url
            )
            result[match[1]] = sub_resource if sub_resource else {
                'href': str(sub_rel_url),
                'name': match[1]
            }
        return result


class PlainView(View):
    """

    .. deprecated::

        Functionality of classes :class:`DynamicView` and :class:`PlainView` was
        moved into :class:`View`. This class is here only to keep method
        :meth:`all_links` around.

    """


    async def all_links(self):
        # language=rst
        """Overrides :meth:`Resource.all_links`.

        This default implementation returns "subresources" of ``self``
        found in the router.

        Some subclasses may want to override this method.

        """
        result = {}
        # noinspection PyUnresolvedReferences
        path = _slashify(self.resource().get_info()['path'])
        for aiohttp_resource in self.request.app.router.resources():
            if not isinstance(aiohttp_resource, web.PlainResource):
                continue
            sub_path = aiohttp_resource.get_info()['path']
            if not sub_path.startswith(path):
                continue
            match = self.SEGMENT_RE.match(sub_path, len(path))
            if match is None:
                continue
            sub_rel_url = web.URL(_slashify(self.rel_url.raw_path) + match[0])
            sub_rel_url = self.add_embed_to_url(sub_rel_url, match[0])
            sub_resource = self.construct_resource_for(
                self.request, sub_rel_url
            )
            result[match[1]] = sub_resource if sub_resource else {
                'href': str(sub_rel_url),
                'name': match[1]
            }
        return result
