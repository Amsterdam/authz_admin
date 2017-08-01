import logging
import typing as T
import re
import base64
import struct
import json
import hashlib
from collections.abc import Mapping

from aiohttp import web

_logger = logging.getLogger(__name__)

ETag = T.Union[str, bool, None]
_ETAGS_PATTERN = re.compile(
    r'\s*(?:W/)?"[\x21\x23-\x7e\x80-\xff]+"(?:\s*,\s*(?:W/)?"[\x21\x23-\x7e\x80-\xff]+")*'
)
_ETAG_ITER_PATTERN = re.compile(
    r'\s*,\s*((?:W/)?"[\x21\x23-\x7e\x80-\xff]+")'
)
_STAR = '*'
_HTTP_UNSAFE_METHODS = {'DELETE', 'PATCH', 'POST', 'PUT'}
VALID_ETAG_PATTERN = re.compile(r'(?:W/)?"[\x21\x23-\x7e\x80-\xff]+"')


def _parse_if_header(request: web.Request, header_name: str) -> T.Union[None, str, T.Set]:
    if header_name not in request.headers:
        return None
    header = ','.join(request.headers.getall(header_name))
    if header == _STAR:
        return _STAR
    if not _ETAGS_PATTERN.fullmatch(header):
        raise web.HTTPBadRequest(
            text="Syntax error in request header If-Match: %s" % header
        )
    return set({
        match[1] for match in _ETAG_ITER_PATTERN.finditer(header)
    })


def _if_match(request: web.Request) -> T.Callable[[ETag], None]:
    # The If-Match: header is used in non-safe HTTP requests to prevent lost
    # update problems.
    etags = _parse_if_header(request, 'If-Match')

    def if_match(etag: ETag):
        if etags is None:
            return
        if etag is False:
            raise web.HTTPNotFound()
        if etag is None:
            raise web.HTTPPreconditionFailed(
                text="Resource doesn't support If-Match header."
            )
        # From here on, etag is either a string or True:
        if isinstance(etags, set):
            if etag is True:
                raise web.HTTPPreconditionFailed(
                    text="Resource doesn't support If-Match header."
                )
            if etag not in etags:
                raise web.HTTPPreconditionFailed()
    return if_match


def _if_none_match(request: web.Request) -> T.Callable[[ETag], None]:
    # The If-None-Match: header is used in two scenarios:
    # 1. GET requests by a caching client. In this case, the client will
    #    normally provide a list of (cached) ETags.
    # 2. PUT requests, where the client intends to create a new resource and
    #    wants to avoid overwriting an existing resource. In this case, the
    #    client will normally provide only the asterisk "*" character.
    etags = _parse_if_header(request, 'If-None-Match')

    def if_none_match(etag: ETag):
        if etags is None or etag is False:
            return
        if etag is None:
            raise web.HTTPPreconditionFailed(
                text="Resource doesn't support If-Match header."
            )
        # From here on, we know that etag is True or a string:
        if etags is _STAR:
            raise web.HTTPPreconditionFailed()
        # From here on, we know that etags is a set of strings.  So, the client
        # gave a list of ETags that must NOT match (which indicates it's a
        # caching client) and we have one of three cases:
        # 1. etag is a valid etag string.  We must fail if it's supplied by
        #    the client.
        # 2. etag is False, meaning the resource doesn't exist.  In this
        #    case, the condition is met.
        # 3. etag is True, meaning the resource exists but doesn't support
        #    etags.  This is a tricky case.  None of the supplied ETags
        #    matches, so strictly speaking the condition is met.   One might
        #    argue, however, that ALL conditional requests should fail on
        #    existing resources without an ETag.  To be on the safe side, we
        #    fail on non-safe requests:
        if (
            isinstance(etag, str) and etag in etags
        ) or (
            etag is True and
            request.method.upper() in _HTTP_UNSAFE_METHODS
        ):
            raise web.HTTPPreconditionFailed()
    return if_none_match


def assert_preconditions(request: web.Request):
    if_match = _if_match(request)
    if_none_match = _if_none_match(request)

    def assert_preconditions(etag: ETag):
        if_match(etag)
        if_none_match(etag)

    return assert_preconditions


def etaggify(v: str, weak) -> str:
    weak = 'W/' if weak else ''
    return weak + '"' + v + '"'


def etag_from_int(value: int, weak=False) -> str:
    assert value >= 0
    if value <= 0xff:
        format = 'B'
    elif value <= 0xffff:
        format = 'H'
    elif value <= 0xffffffff:
        format = 'L'
    else:
        format = 'Q'
    return etaggify(
        base64.urlsafe_b64encode(struct.pack(format, value)).decode(),
        weak
    )


def etag_from_float(value: float, weak=False) -> str:
    return etaggify(
        base64.urlsafe_b64encode(struct.pack('d', value)).decode(),
        weak
    )


def _json_dumps_default(value):
    if isinstance(value, Mapping):
        return dict(value)
    raise TypeError()


class ETagGenerator:
    def __init__(self):
        self._hash = hashlib.sha3_224()

    def update(self, v):
        self._hash.update(
            json.dumps(v, ensure_ascii=False, sort_keys=True, default=_json_dumps_default).encode()
        )
        return self

    @property
    def etag(self, weak=False):
        return etaggify(
            base64.urlsafe_b64encode(self._hash.digest()).decode(),
            weak
        )
