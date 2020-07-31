from aiohttp import web

from core.database import init_db
from core.routes import init_routes

app = web.Application()
app.on_startup.append(init_db)
app.on_startup.append(init_routes)

if __name__ == '__main__':
    web.run_app(app)
