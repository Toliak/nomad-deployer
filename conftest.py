import pytest
from sqlalchemy import create_engine
from sqlalchemy_aio import ASYNCIO_STRATEGY

from core import settings


@pytest.fixture
def prepare_db():
    with create_engine(settings.connection_uri, strategy=ASYNCIO_STRATEGY) as engine:
        async with engine.connect() as conn:
            await conn.execute("TRUNCATE TABLE 'jwt_role'")
            await conn.execute("TRUNCATE TABLE 'jwt_config'")
