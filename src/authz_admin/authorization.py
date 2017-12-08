import logging
import re
import typing as T
import functools

from aiohttp import web
import jwt

from rest_utils._view import View

_logger = logging.getLogger(__name__)


async def _extract_scopes(request: web.Request,
                          _security_scheme: T.Dict) -> T.Set:

    authorization_header = request.headers.get('authorization')
    if authorization_header is None:
        return set()
    match = re.fullmatch(r'bearer ([-\w.=]+)', authorization_header, flags=re.IGNORECASE)
    if not match:
        return set()

    token = match[1]
    try:
        header = jwt.get_unverified_header(token)
    except (jwt.InvalidTokenError, jwt.DecodeError):
        raise web.HTTPBadRequest(text='API authz problem: JWT decode error while reading header') from None

    if 'kid' not in header:
        raise web.HTTPBadRequest(text='API authz problem: Did not get a valid key identifier') from None

    keys = request.app['jwks'].verifiers

    if header['kid'] not in keys:
        raise web.HTTPBadRequest(text="API authz problem: Unknown key identifier: {}".format(header['kid'])) from None
    key = keys[header['kid']]
    try:
        access_token = jwt.decode(
            token, verify=True,
            key=key.key,
            algorithms=key.alg
        )
    except jwt.InvalidTokenError as e:
        raise web.HTTPBadRequest(text='Invalid Bearer token') from None
    if 'scopes' not in access_token or not isinstance(access_token['scopes'], list):
        raise web.HTTPBadRequest(
            text='No scopes in access token'
        )
    return set(access_token['scopes'])


async def _extract_api_key_info(request: web.Request,
                                security_scheme: T.Dict) -> T.Any:
    assert security_scheme['in'] == 'header'
    assert security_scheme['name'] == 'Authorization'
    authorization_header = request.headers.get('authorization')
    if authorization_header is None:
        return False
    match = re.fullmatch(r'apikey ([-\w]+=*)', authorization_header)
    if not match:
        return False
    return match[1] == request.app['config']['authz_admin']['api_key']


async def _extract_authz_info(request: web.Request,
                              security_definitions: T.Dict[str, T.Dict[str, T.Any]]):
    result = {}
    for key, security_scheme in security_definitions.items():
        security_type = security_scheme['type']
        if security_type == 'oauth2':
            result[key] = await _extract_scopes(request, security_scheme)
        elif security_type == 'apiKey':
            result[key] = await _extract_api_key_info(request, security_scheme)
        else:
            _logger.error('Unknown security type: %s' % security_type)
            raise web.HTTPInternalServerError()
    return result


async def middleware(app: web.Application, handler):
    async def middleware_handler(request: web.Request) -> web.Response:
        swagger = app['swagger']
        security_definitions = swagger.specification['securityDefinitions']
        request['authz_info'] = await _extract_authz_info(request, security_definitions)

        return await handler(request)
    return middleware_handler


async def enforce_one_of(request: web.Request,
                         security_requirements: T.List[T.Dict[str, T.Optional[T.Iterable]]]):
    for security_requirement in security_requirements:
        if await _enforce_all_of(request, security_requirement):
            return
    raise web.HTTPUnauthorized()


async def _enforce_all_of(request: web.Request,
                          security_requirements: T.Dict[str, T.Optional[T.Iterable]]) -> bool:
    swagger = request.app['swagger']
    security_definitions = swagger.specification['securityDefinitions']
    for requirement, scopes in security_requirements.items():
        authz_info = request['authz_info'][requirement]
        security_type = security_definitions[requirement]['type']
        if security_type == 'oauth2':
            if len(set(scopes) - authz_info) > 0:
                return False
        elif security_type == 'apiKey':
            if not authz_info:
                return False
        else:
            _logger.error('Unexpected security type: %s' % security_type)
            raise web.HTTPInternalServerError()
    return True


def authorize(p_method=None):
    def decorator(f: T.Callable):
        @functools.wraps(f)
        async def wrapper(self: View, *args, **kwargs):
            swagger = self.request.app['swagger']
            base_path = swagger.base_path
            paths = swagger.specification['paths']
            path, _ = swagger.get_path_spec(
                self.rel_url.raw_path
            )
            assert path is not None
            assert path.startswith(base_path)
            path = path[len(base_path):]
            method = p_method or self.request.method
            if method.lower() not in paths[path]:
                raise web.HTTPMethodNotAllowed(
                    method, list([
                        method.upper() for method in paths[path].keys()
                    ])
                )
            method_info = paths[path][method.lower()]
            if 'security' in method_info:
                await enforce_one_of(self.request, method_info['security'])
            return await f(self, *args, **kwargs)
        return wrapper
    return decorator
