import json

from aiohttp import web
from aiohttp.web_exceptions import HTTPException
from aiohttp.web_urldispatcher import View
from sqlalchemy import select, insert
from sqlalchemy.engine import RowProxy
from sqlalchemy_aio.base import AsyncResultProxy

from core import settings
from core.exceptions import HTTPApiAdminTokenInvalid
from core.tables import JwtRole


class ConfigView(View):
    async def post(self):
        expected_token = settings.admin_token

        data = await self.request.json()
        token = data.get('token', None)
        if token != expected_token:
            raise HTTPApiAdminTokenInvalid()

        role = self.request.match_info.get('role_name', '')
        query = select([JwtRole]).where(JwtRole.role == role)

        async with self.request.app['db'].connect() as conn:
            row: AsyncResultProxy = await conn.execute(query)

            result: RowProxy = await row.fetchone()
            if result is not None:
                return web.Response(text=json.dumps(
                    dict(id=result.id, )
                ))

            result: AsyncResultProxy = await conn.execute(
                insert(JwtRole).values(dict(role=role,
                                            bound_claims='sample text'))
            )
            return web.Response(text=json.dumps(
                dict(id=result.inserted_primary_key[0], )
            ))
