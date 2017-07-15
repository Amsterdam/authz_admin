from aiohttp import web

from oauth2.authz_admin_service import resource_types

resource = resource_types.DynamicResource('/datasets/{dataset}')
