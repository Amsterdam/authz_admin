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
    accept = ','.join(request.headers.getall('ACCEPT', ['*/*']))
    mime_types = [
        part.split(';', 2)[0].strip() for part in accept.split(',')
    ]
    if not HAL_JSON_COMPATIBLE.isdisjoint(mime_types):
        return "application/hal+json; charset=UTF-8"
    elif "application/json" in mime_types:
        return "application/json; charset=UTF-8"
    else:
        body = ",".join(AVAILABLE_CONTENT_TYPES).encode('ascii')
        raise web.HTTPNotAcceptable(
            body=body,
            content_type='text/plain; charset="US-ASCII"'
        )
