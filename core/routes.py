from aiohttp import web

from core.controllers import ConfigController

async def init_routes(app):
    app.add_routes([web.get('/role/{role_name}', ConfigController.as_handle()), ])
