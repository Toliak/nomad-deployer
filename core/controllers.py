import json

from aiohttp import web
from aiohttp.web_request import Request
from sqlalchemy import select, insert
from sqlalchemy.engine import RowProxy
from sqlalchemy_aio.base import AsyncResultProxy

from core.exceptions import ApiException, response_internal_error, MethodNotAllowedApiException
from core.tables import JwtRole


class DefaultController:
    def __init__(self):
        pass

    @classmethod
    def as_handle(cls):
        async def bundle_function(*args, **kwargs):
            this = cls()
            return await this.route(*args, **kwargs)

        return bundle_function

    async def route(self, request: Request, *args, **kwargs):
        method = request.match_info.route.method
        try:
            if method == 'GET':
                return await self.get(request, *args, **kwargs)
            if method == 'POST':
                return await self.post(request, *args, **kwargs)
            if method == 'PUT':
                return await self.put(request, *args, **kwargs)
            if method == 'DELETE':
                return await self.delete(request, *args, **kwargs)
        except ApiException as e:
            return e.to_response()
        except Exception as e:
            return response_internal_error(e)

    async def get(self, request: Request, *args, **kwargs):
        raise MethodNotAllowedApiException('GET')

    async def post(self, request: Request, *args, **kwargs):
        raise MethodNotAllowedApiException('POST')

    async def put(self, request: Request, *args, **kwargs):
        raise MethodNotAllowedApiException('PUT')

    async def delete(self, request: Request, *args, **kwargs):
        raise MethodNotAllowedApiException('DELETE')


class ConfigController(DefaultController):
    async def get(self, request: Request, *args, **kwargs):
        role = request.match_info.get('role_name', '')
        query = select([JwtRole]).where(JwtRole.role == role)

        async with request.app['db'].connect() as conn:
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
