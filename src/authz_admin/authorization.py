from aiohttp import web

# noinspection PyUnusedLocal
async def middleware(app: web.Application, handler):
    async def middleware_handler(request: web.Request) -> web.Response:
        return await handler(request)
    return middleware_handler
