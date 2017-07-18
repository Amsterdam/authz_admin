# languege=rst
"""

This module contains some aiohttp-related utils for:

Content negotiation
    See :func:`best_content_type`.

"""
import inspect
import logging
import re
from collections.abc import Mapping

from aiohttp import web

from . import json as ajson
from .embed import parse as parse_embed

_logger = logging.getLogger(__name__)


# ┏━━━━━━━━━━━━━━━━━━━━━┓
# ┃ Content Negotiation ┃
# ┗━━━━━━━━━━━━━━━━━━━━━┛


AVAILABLE_CONTENT_TYPES = (
    "application/hal+json",
    "application/json",
)
HAL_JSON_COMPATIBLE = {
    "application/hal+json",
    "application/*",
    "*/*"
}


def best_content_type(request):
    # language=rst
    """The best matching Content-Type.

    :param aiohttp.web.Request request:
    :rtype: str
    :raises: :ref:`aiohttp.web.HTTPNotAcceptable <aiohttp-web-exceptions>` if
        none of the available content types are acceptable by the client.

    """
    mime_types = [
        part.split(';', 2)[0].strip() for part in request.headers.get('ACCEPT', '*/*').split(',')
    ]
    if not HAL_JSON_COMPATIBLE.isdisjoint(mime_types):
        return "application/hal+json; charset=UTF-8"
    elif "application/json" in mime_types:
        return "application/json; charset=UTF-8"
    else:
        body = "\n".join(AVAILABLE_CONTENT_TYPES).encode('ascii')
        raise web.HTTPNotAcceptable(
            body=body,
            content_type='text/plain; charset="US-ASCII"'
        )


async def _raw_path_to_resource(raw_path, router):
    for resource in router.resources():
        if isinstance(resource, _ResourceMixin) and resource.match(raw_path):
            return resource


class _ResourceMixin:
    # language=rst
    """

    **Responsibilities**

    *   Content negotiation
    *   Handling GET requests

    .. todo::

        1.  Handling conditional requests (ie. with `If-*` request headers.

    """

    def match(self, raw_path):
        # noinspection PyUnresolvedReferences
        return self._match(raw_path)

    @classmethod
    def best_content_type(cls, request):
        # language=rst
        """The best matching Content-Type."""
        mime_types = [
            part.split(';', 2)[0].strip() for part in request.headers.get('ACCEPT', '*/*').split(',')
        ]
        if not HAL_JSON_COMPATIBLE.isdisjoint(mime_types):
            return "application/hal+json; charset=UTF-8"
        elif "application/json" in mime_types:
            return "application/json; charset=UTF-8"
        else:
            body = "\n".join(AVAILABLE_CONTENT_TYPES).encode('ascii')
            raise web.HTTPNotAcceptable(
                body=body,
                content_type='text/plain; charset="US-ASCII"'
            )

    async def http_get(self, request):
        # language=rst
        """aiohttp request handler for the GET method.


        :param aiohttp.web.Request request:
        :rtype: aiohttp.web.Response

        """
        response = web.StreamResponse()

        response.content_type = self.best_content_type(request)

        await response.prepare(request)
        async for chunk in ajson.encode(await self.to_dict(request)):
            response.write(chunk)
            await response.drain()
        response.write_eof()
        return response

    def name_for(self, raw_path):
        # noinspection PyUnresolvedReferences
        return self.name

    async def to_dict(self, request, rel_url=None, embed=None):
        """

        :param aiohttp.web.Request request:
        :param aiohttp.web.URL rel_url:
        :param dict embed:

        """
        if rel_url is None:
            rel_url = request.rel_url
            embed = parse_embed(
                ','.join(request.headers.getall('embed'))
            )

        # noinspection PyUnresolvedReferences
        result = await self.attributes(request, rel_url)
        embedded = {}
        # noinspection PyUnresolvedReferences
        result['_links'] = await self.links(request, rel_url)
        if 'self' not in result['_links']:
            result['_links']['self'] = {
                'href': str(rel_url),
                'name': self.name_for(rel_url.raw_path)
            }
        # Embed links as requested:
        for link_name in list(result['_links'].keys()):
            sub_embed = embed.get(link_name, embed.get('*', None))
            if sub_embed is not None:
                embedded[link_name] = _embedded(
                    result['_links'].pop(link_name),
                    request, rel_url, sub_embed
                )
        if len(embedded) > 0:
            result['_embedded'] = embedded
            for e in embedded:
                result['_embedded'][e] = _embedded(embedded)
            result['_embedded'] = _embedded(embedded, request, rel_url, embed)
            links = result['_links'][link_name]
            if isinstance(links, Mapping):
                url = rel_url.join(web.URL(links['href']))
                resource = _raw_path_to_resource(url.raw_path, request.app.router)
                if resource:
                    result['_embedded'][link_name] = resource.to_dict(request, rel_url=url, embed=sub_embed)
                    del result['_links'][link_name]
            elif inspect.isasyncgen(links):
                async for link in links:
                    url = rel_url.join(web.URL(link['href']))
                    resource = _raw_path_to_resource(url.raw_path, request.app.router)
                    if resource:
                        result['_embedded'][link_name] = resource.to_dict(request, rel_url=url, embed=sub_embed)
                        del result['_links'][link_name]

        # Make proper link objects:
        for link_name in list(result['_links']):
            pass  # TODO: create proper link objects
        return result

    #     # language=rst
    #     """
    #     :param aiohttp.web.Request request:
    #     :param aiohttp.web.Response response:
    #     :return:
    #
    #     """
    #     result = {}
    #     response.write(b'{"_links":{"self":')
    #     response.write(
    #         json.dumps({
    #             'href': str(request.rel_url),
    #             'name': self.name
    #         }, separators=(',', ':')).encode()
    #     )
    #     for name, links in self.links(request):
    #         assert isinstance(name, str)
    #         response.write(b',"' + name.encode() + b'":')
    #         if isinstance(links, dict):
    #             response.write(
    #                 json.dumps(links, separators=(',', ':')).encode()
    #             )
    #         else:
    #             response.write(b'[')
    #             if inspect.isasyncgenfunction(links):
    #                 async for link in links():
    #                     response.write(
    #                         json.dumps(link, separators=(',', ':')).encode() +
    #                         b','
    #                     )
    #                     await response.drain()
    #             else:
    #                 for link in links:
    #                     response.write(
    #                         json.dumps(link, separators=(',', ':')).encode() +
    #                         b','
    #                     )
    #             response.write(b']')
    #     # TODO: stream the _links section, possibly including items.
    #     response.write(b'},')
    #     # TODO: stream the attributes
    #     response.write(b'"_embedded":{')
    #     # TODO: stream the embedded resources
    #
    #     response.write(b'}}')
    #     await response.write_eof()

    def _get_attributes(self):
        async def null_attributes(*_):
            return {}
        if not hasattr(self, '_attributes'):
            return null_attributes
        return self._attributes

    def _set_attributes(self, attributes):
        assert inspect.isawaitable(attributes)
        assert attributes.__code__.co_argcount == 2
        self._attributes = attributes

    attributes = property(fget=_get_attributes, fset=_set_attributes)

    def _get_links(self):
        async def null_links(*_):
            return {}
        if not hasattr(self, '_links'):
            return null_links
        return self._links

    def _set_links(self, links):
        assert inspect.isawaitable(links)
        assert links.__code__.co_argcount == 2
        self._links = links

    links = property(fget=_get_links, fset=_set_links)


class AiohttpDynamicResource (web.DynamicResource):
    def __init__(self, path, *, name=None):
        # language=rst
        """Workaround for ugly design in `aiohttp.web.DynamicResource`.

        This class is exactly like `aiohttp.web.DynamicResource`, except that
        its constructor takes a ``path`` parameter, instead of a ``pattern`` and
        ``formatter``.

        **Rationale**

        Class `aiohttp.web.PlainResource` has the following constructor
        signature::

            def __init__(self, path, *, name=None):
                ...

        One might expect the same signature for `aiohttp.web.DynamicResource`,
        but it has::

            def __init__(self, pattern, formatter, *, name=None):
                ...

        Internally, both these constructors are called from
        `aiohttp.web.UrlDispatcher.add_resource` with signature::

            def add_resource(self, path, *, name=None):
                ...

        In the case of a non-dynamic resource path, this method constructs a
        `aiohttp.web.PlainResource`, passing through the ``path`` parameter. In
        the case of a *dynamic* resource path, method ``add_resource`` first
        computes a ``pattern`` and a ``formatter`` from the ``path`` parameter,
        and then constructs an `aiohttp.web.DynamicResource` with these
        parameters.

        To me, it seems that ``add_resource`` is doing work (computing
        ``pattern`` and ``formatter`` that belongs to the constructor of
        `aiohttp.web.DynamicResource`. If this work is moved there, it has the
        additional benefit of aligning the constructor signatures of
        `aiohttp.web.DynamicResource` and  `aiohttp.web.PlainResource`.

        :param str path:
        :param str name:
        """
        UD = web.UrlDispatcher
        pattern = ''
        formatter = ''
        for part in UD.ROUTE_RE.split(path):
            match = UD.DYN.fullmatch(part)
            if match:
                pattern += '(?P<{}>{})'.format(match.group('var'), UD.GOOD)
                formatter += '{' + match.group('var') + '}'
                continue

            match = UD.DYN_WITH_RE.fullmatch(part)
            if match:
                pattern += '(?P<{var}>{re})'.format(**match.groupdict())
                formatter += '{' + match.group('var') + '}'
                continue

            if '{' in part or '}' in part:
                raise ValueError("Invalid path '{}'['{}']".format(path, part))

            path = web.URL(part).raw_path
            formatter += path
            pattern += re.escape(path)

        try:
            compiled = re.compile(pattern)
        except re.error as exc:
            raise ValueError(
                "Bad pattern '{}': {}".format(pattern, exc)) from None
        super().__init__(compiled, formatter, name=name)


# noinspection PyUnusedLocal
async def _null_list(request):
    if False:
        yield


# noinspection PyUnusedLocal
async def _null_dict(request):
    yield ajson.IM_A_DICT


class _CollectionMixin:

    @property
    def items(self):
        if not hasattr(self, '_items'):
            return _null_list
        return self._items

    @items.setter
    def items(self, items):
        assert inspect.isasyncgenfunction(items)
        self._items = items


class PlainResource (web.PlainResource, _ResourceMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_route('GET', self.http_get)


class DynamicResource (AiohttpDynamicResource, _ResourceMixin):
    def __init__(self, *args, name_for=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_route('GET', self.http_get)
        self._name_for = name_for or ('name' in kwargs and "{%s}" % kwargs['name']) or None

    def name_for(self, raw_path):
        self._name_for.format_map(self.match(raw_path))


class PlainCollection (PlainResource, _CollectionMixin):
    pass


class DynamicCollection (DynamicResource, _CollectionMixin):
    pass
