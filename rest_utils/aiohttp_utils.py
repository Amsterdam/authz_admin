# languege=rst
"""

This module contains some aiohttp-related utils for:

Content negotiation
    See :func:`best_content_type`.

"""
import json as ajson
import logging
import re

from aiohttp import web

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

    .. todo:: Generalize. (Now, we only negotiate hal+json and friends.)

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
