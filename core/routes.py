from core.controllers import RoleView, RoleListView


async def init_routes(app):
    app.router.add_view('/role/', RoleListView)
    app.router.add_view('/role/{role_name}', RoleView)
