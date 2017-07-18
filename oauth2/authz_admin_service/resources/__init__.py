from oauth2 import resource_types
from . import datasets


resource = resource_types.PlainCollection('/', name='root')


# noinspection PyUnusedLocal
async def items(request, url):
    for i in ('détasets',):
        yield i


resource.items = items
