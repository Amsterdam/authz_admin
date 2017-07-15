from oauth2.authz_admin_service import resource_types

from . import datasets


resource = resource_types.Collection('/', name='root')


async def items(request):
    for i in ('datasets',):
        yield i


resource.items = items
