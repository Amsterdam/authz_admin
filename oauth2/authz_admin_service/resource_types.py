import inspect
import logging
import traceback
import re
import json
import abc

from aiohttp import web

_logger = logging.getLogger(__name__)

AVAILABLE_CONTENT_TYPES = (
    "application/hal+json",
    "application/json",
)
HAL_JSON_COMPATIBLE = {
    "application/hal+json",
    "application/*",
    "*/*"
}


class _ResourceMixin:

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
                body=b"application/hal+json,application/json",
                content_type='text/plain; charset="US-ASCII"'
            )

    async def http_get(self, request):
        # language=rst
        """
        :param aiohttp.web.Request request:
        :rtype: aiohttp.web.Response

        """
        response = web.StreamResponse()
        response.content_type = self.best_content_type(request)
        await self.stream_json(request, response)
        return response

    async def stream_json(self, request, response):
        # language=rst
        """
        :param aiohttp.web.Request request:
        :param aiohttp.web.Response response:
        :return:

        """
        await response.prepare(request)
        response.write(b'{"_links":{"self":')
        response.write(
            json.dumps({
                'href': str(request.rel_url),
                'name': self.name
            }, separators=(',', ':')).encode()
        )
        for name, links in self.links(request):
            assert isinstance(name, str)
            response.write(b',"' + name.encode() + b'":')
            if isinstance(links, dict):
                response.write(
                    json.dumps(links, separators=(',', ':')).encode()
                )
            else:
                response.write(b'[')
                if inspect.isasyncgenfunction(links):
                    async for link in links():
                        response.write(
                            json.dumps(link, separators=(',', ':')).encode() +
                            b','
                        )
                        await response.drain()
                else:
                    for link in links:
                        response.write(
                            json.dumps(link, separators=(',', ':')).encode() +
                            b','
                        )
                response.write(b']')
        # TODO: stream the _links section, possibly including items.
        response.write(b'},')
        # TODO: stream the attributes
        response.write(b'"_embedded":{')
        # TODO: stream the embedded resources

        response.write(b'}}')
        await response.write_eof()

    def links(self, request):
        return []

# noinspection PyUnusedLocal
async def _null_items(request):
    _logger.warning("Attribute 'items' not set.\n%s", traceback.format_stack())
    if False:
        yield


class Collection (web.PlainResource, _ResourceMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._items = _null_items
        self.add_route('GET', self.http_get)

    def _get_items(self):
        return self._items

    def _set_items(self, items):
        assert inspect.isasyncgenfunction(items)
        self._items = items

    items = property(fget=_get_items, fset=_set_items)

    def links(self, request):
        pass


class DynamicResource (web.DynamicResource, _ResourceMixin):
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
        self.add_route('GET', self.http_get)
