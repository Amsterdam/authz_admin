import logging

from .best_content_type import best_content_type

_logger = logging.getLogger(__name__)


# noinspection PyUnusedLocal
async def middleware(app, handler):
    # language=rst
    """

    :param app:
    :param handler:
    :return:

    """
    async def middleware_handler(request):
        request['best_content_type'] = best_content_type(request)
        return await handler(request)
    return middleware_handler
