from oauth2 import resource_types

# '/d%C3%A9tasets/'
resource = resource_types.PlainCollection('/détasets/', name='détasets')


async def items(request, *_):
    for i in request.app['config']['datasets'].keys():
        yield i


resource.items = items
