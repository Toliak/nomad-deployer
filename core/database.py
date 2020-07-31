from sqlalchemy import (
    create_engine)
from sqlalchemy_aio import ASYNCIO_STRATEGY

from core import settings


async def init_db(app):
    # app['db'] = await aiopg_sqlite.create_engine(**settings.connection_params, loop=app.loop)
    app['db'] = create_engine(
        # In-memory sqlite database cannot be accessed from different
        # threads, use file.
        settings.connection_uri, strategy=ASYNCIO_STRATEGY
    )
