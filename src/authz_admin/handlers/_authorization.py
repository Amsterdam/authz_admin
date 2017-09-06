import logging
import re

from aiohttp import web

from authz_admin import config

_logger = logging.getLogger(__name__)

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
                text="Syntax error in 'scopes' query parameter."
            )
    else:
        _logger.debug("all_scopes: %s", config.all_scopes(request.app['config']))
        scope = ' '.join(config.all_scopes(request.app['config']))
    location = web.URL(request.query['redirect_uri'], strict=True)
    location = location.update_query(
        access_token=access_token(scope, 'test123').decode(),
        token_type='bearer',
        scope=scope
    )
    if 'state' in request.query:
        location = location.update_query(state=request.query['state'])
    _logger.debug("location: %s", location)
    return web.Response(
        status=302,
        headers={
            'Location': str(location)
        }
    )


