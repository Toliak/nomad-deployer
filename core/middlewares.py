import logging

from aiohttp import web
from aiohttp.web_exceptions import HTTPException


@web.middleware
async def reformat_error_to_json(request, handler):
    try:
        return await handler(request)
    except HTTPException as e:
        return web.json_response(dict(detail=e.reason,
                                      status=e.status_code),
                                 status=e.status_code)
    except Exception as e:
        logging.exception("Internal error")
        return web.json_response(dict(detail=f'Internal Server Error: {str(e)}',
                                      status=500),
                                 status=500)


async def init_middlewares(app):
    app.middlewares.extend([reformat_error_to_json])
