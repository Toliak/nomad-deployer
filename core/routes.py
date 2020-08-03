from core.controllers import RoleView, RoleListView, ConfigView, RunView


async def init_routes(app):
    app.router.add_view('/role/', RoleListView)
    app.router.add_view('/role/{role_name}', RoleView)
    app.router.add_view('/config/', ConfigView)
    app.router.add_view('/run/', RunView)
