from aiohttp import web

from core.database import init_db
from core.middlewares import init_middlewares
from core.routes import init_routes


def create_app(loop=None):
    if loop:
        app = web.Application(loop=loop)
    else:
        app = web.Application()

    app.on_startup.append(init_db)
    app.on_startup.append(init_routes)
    app.on_startup.append(init_middlewares)

    return app


if __name__ == '__main__':
    app = create_app()
    web.run_app(app)
