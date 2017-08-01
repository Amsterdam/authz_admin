"""Middleware that parses the 'embed=...' query parameter."""

import re
import logging
from collections import deque

from aiohttp import web

_logger = logging.getLogger(__name__)


_EMBED_TOKEN = re.compile(',?[a-z_]\\w*|\\?[^,()]*|,?\\*|[()]', flags=re.IGNORECASE)
"""Used only by :func:`_tokenize_embed`."""


def _tokenize_embed(s):
    # language=rst
    """Tokenizer for the 'embed' query parameter.

    Used exclusively by :func:`parse`.

    Possible tokens are:

    identifier
        always starts with an underscore '_' or an alphabetical character,
        followed by zero or more underscores, alphabetical characters or digits.
        Examples: ``foo``, ``_BAR``, ``f00_123``
    query string
        always starts with a question mark.
    punctuation character
        either ``(``, ``)`` or ``*``

    For each token found, this generator yields a tuple ``(token, pos)`` with
    the token string and the position at which the token was found.

    Example::

        list(_tokenize_embed('foo?a=b(bar,*)'))
        >>> [('foo', 0), ('?a=b', 3), ('(', 7), ('bar', 8), ('*', 11), (')', 13)]

    :param str s:
    :yields: tuple(token: str, pos: int)
    :raises: :ref:`HTTPBadRequest <aiohttp-web-exceptions>` if a syntax error is
        detected.

    """
    pos = 0
    for match in _EMBED_TOKEN.finditer(s):
        if match.start() != pos:
            raise web.HTTPBadRequest(
                text="Syntax error in query parameter 'embed' at position %d" % pos
            )
        token = match[0]
        if token[:1] == ',':
            token = token[1:]
        yield token, pos
        pos = match.end()
    if pos != len(s):
        raise web.HTTPBadRequest(
            text="Syntax error in query parameter 'embed' at position %d" % pos
        )


def parse(request):
    # language=rst
    """Parser for the 'embed' query parameter.

    Example::

        parse('foo?a=b&c=d(bar,*)')
        >>> {'foo': {'_query': '?a=b', 'bar': {}, '*': {}}}

    :param aiohttp.web.Request request:
    :rtype: dict
    :raises: :ref:`HTTPBadRequest <aiohttp-web-exceptions>` if a syntax error is
        detected.

    """
    result = {}
    if 'swagger_query' not in request:
        _logger.warning("'swagger_query' not found in request.")
    query = request.get('swagger_query', request.query)
    embed = ','.join(query.getall('embed', default=[]))
    if len(embed) == 0:
        return result
    stack = deque()
    stack.appendleft(result)
    current = None
    for token, pos in _tokenize_embed(embed):
        if token == '(':
            if current is None:
                raise web.HTTPBadRequest(
                    text="Unexpected opening parenthesis in query parameter 'embed' at position %d" % pos
                )
            stack.appendleft(stack[0][current])
            current = None
            pass
        elif token == ')':
            stack.popleft()
            if len(stack) == 0:
                raise web.HTTPBadRequest(
                    text="Unmatched closing parenthesis in query parameter 'embed' at position %d" % pos
                ) from None
        elif token[:1] == '?':
            if current is None:
                raise web.HTTPBadRequest(
                    text="Unexpected query string '%s' in query parameter 'embed' at position %d" % (token, pos)
                )
            stack[0][current]['_query'] = token
        else:
            if token in stack[0]:
                raise web.HTTPBadRequest(
                    text="Link name '%s' mentioned more than once in query parameter 'embed' at position %d" % (token, pos)
                )
            if token in ('self', 'collection', 'up'):
                raise web.HTTPBadRequest(
                    text="Resource relation '%s' can not be embedded" % token
                )
            current = token
            stack[0][token] = {}
    if len(stack) > 1:
        raise web.HTTPBadRequest(
            text="Missing closing parenthesis in query parameter 'embed'"
        )
    return result


# noinspection PyUnusedLocal
async def middleware(app, handler):
    async def middleware_handler(request):
        request['embed'] = parse(request)
        return await handler(request)
    return middleware_handler
