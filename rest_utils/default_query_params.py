import logging

from swagger_parser import SwaggerParser
from aiohttp import web
from typing import Dict

_logger = logging.getLogger(__name__)


def default_query_params(request: web.Request, raw_path: str) -> Dict[str, str]:
    if 'swagger' not in request.app:
        _logger.warning('No swagger definition file found in application.')
        return {}
    swagger: SwaggerParser = request.app['swagger']
    path, path_info = swagger.get_path_spec(
        raw_path,
        action=request.method.lower()
    )
    if path is None:
        return {}
    return dict({
        param: param_info['default']
        for param, param_info in path_info.get('parameters', {}).items()
        if 'default' in param_info
    })
