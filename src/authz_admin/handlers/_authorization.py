import logging
import re
import math
import time
import typing as T

from aiohttp import web
import jwt

from authz_admin import config

_logger = logging.getLogger(__name__)


def access_token(scope: str, jwks) -> bytes:
    jwks_signers = jwks.signers
    assert len(jwks_signers) > 0

    list_signers = [(k, v) for k, v in jwks_signers.items()]
    (kid, key) = list_signers[len(list_signers) - 1]
    header = {"kid": kid}

    scopes = scope.split(' ')
    _logger.debug("Added scopes: %s" % scopes)
    return jwt.encode({
        'sub': 'dp:datapunt@amsterdam.nl',
        'iat': math.floor(time.time()) - 5,
        'exp': math.floor(time.time()) + 3600 * 12,
        'scopes': scopes
    }, key=key.key, alg=key.alg, headers=header)


# If this method is used the JWKS key provide in PUB_JWKS environment should contain
# a private key or be symmetric encoding
async def authorization(request: web.Request) -> web.Response:
    if (request.query.get('response_type') != 'token' or
                'redirect_uri' not in request.query):
        raise web.HTTPBadRequest(
            text="Response type isn't 'token' or no redirect URI provided."
        )
    if 'scope' in request.query:
        scope = request.query['scope']
        if not re.fullmatch(r'[\x21\x23-\x5a\x5e-\x7e\[\]]+(?: [\x21\x23-\x5a\x5e-\x7e\[\]]+)*', scope):
            raise web.HTTPBadRequest(
                text="Syntax error in 'scope' query parameter."
            )
    else:
        _logger.debug("all_scopes: %s", config.all_scopes(request.app['config']))
        scope = ' '.join(config.all_scopes(request.app['config']))
    location = web.URL(request.query['redirect_uri'], strict=True)
    location = location.update_query(
        access_token=access_token(
            scope,
            request.app['jwks']
        ).decode(),
        token_type='bearer',
        scope=scope
    )
    if 'state' in request.query:
        location = location.update_query(state=request.query['state'])
    return web.Response(
        status=302,
        headers={
            'Location': str(location)
        }
    )


