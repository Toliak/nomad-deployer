from core.controllers import ConfigView


async def init_routes(app):
    app.router.add_view('/role/{role_name}', ConfigView)
