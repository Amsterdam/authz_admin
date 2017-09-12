from aiohttp import web

# noinspection PyUnusedLocal
async def authorization(app: web.Application, handler):
    async def middleware_handler(request: web.Request) -> web.Response:
        path, path_info = request.app['swagger'].get_path_spec(
            request.raw_path,
            action=request.method.lower()
        )

        return await handler(request)
    return middleware_handler
