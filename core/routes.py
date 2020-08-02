from core.controllers import RoleView, RoleListView, ConfigView


async def init_routes(app):
    app.router.add_view('/role/', RoleListView)
    app.router.add_view('/role/{role_name}', RoleView)
    app.router.add_view('/config/', ConfigView)
