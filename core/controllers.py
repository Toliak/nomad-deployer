import json
from json import JSONDecodeError

from aiohttp import web
from aiohttp.web_exceptions import HTTPNotFound
from aiohttp.web_urldispatcher import View
from sqlalchemy import select, insert, delete
from sqlalchemy.engine import RowProxy
from sqlalchemy_aio.base import AsyncResultProxy

from core import settings
from core.exceptions import HTTPApiAdminTokenInvalid, HTTPApiRoleAlreadyExists, HTTPApiRoleDataInvalid, \
    HTTPApiRoleNotExist, HTTPApiBoundClaimsValidationError, HTTPApiNomadClaimsValidationError
from core.services import BoundClaimsService, NomadClaimsService
from core.tables import JwtRole


class AdminView(View):
    async def _iter(self):
        expected_token = settings.admin_token
        token = self.request.headers.get('Authorization', '')
        if token != f'Bearer {expected_token}':
            raise HTTPApiAdminTokenInvalid()

        return await super()._iter()


class RoleListView(AdminView):
    async def get(self):
        if self.request.query.get('list') is None:
            raise HTTPNotFound()

        query = select([JwtRole]).limit(1000)
        async with self.request.app['db'].connect() as conn:
            row: AsyncResultProxy = await conn.execute(query)
            result: RowProxy = await row.fetchall()

            response_list = []
            for value in result:
                response_list.append(dict(id=value.id,
                                          role=value.role))

            return web.json_response(response_list)


class RoleView(AdminView):
    async def put(self):
        data = await self.request.json()
        bound_claims = data.get('bound_claims', None)
        if bound_claims is None:
            raise HTTPApiRoleDataInvalid('bound_claims')
        nomad_claims = data.get('nomad_claims', None)
        if nomad_claims is None:
            raise HTTPApiRoleDataInvalid('nomad_claims')
        role = self.request.match_info.get('role_name', None)
        if role is None:
            raise HTTPApiRoleDataInvalid('role_name')

        query = select([JwtRole]).where(JwtRole.role == role)
        async with self.request.app['db'].connect() as conn:
            row: AsyncResultProxy = await conn.execute(query)

            result: RowProxy = await row.fetchone()
            if result is not None:
                raise HTTPApiRoleAlreadyExists(role)

            try:
                BoundClaimsService.validate(json.loads(bound_claims))
            except JSONDecodeError:
                raise HTTPApiBoundClaimsValidationError('ROOT')

            try:
                NomadClaimsService.validate(json.loads(nomad_claims))
            except JSONDecodeError:
                raise HTTPApiNomadClaimsValidationError('ROOT')

            result: AsyncResultProxy = await conn.execute(
                insert(JwtRole).values(dict(role=role,
                                            bound_claims=bound_claims,
                                            nomad_claims=nomad_claims))
            )
            return web.json_response(dict(id=result.inserted_primary_key[0], ))

    async def get(self):
        role = self.request.match_info.get('role_name', None)
        if role is None:
            raise HTTPApiRoleDataInvalid('role_name')

        query = select([JwtRole]).where(JwtRole.role == role)
        async with self.request.app['db'].connect() as conn:
            row: AsyncResultProxy = await conn.execute(query)

            result: RowProxy = await row.fetchone()
            if result is None:
                raise HTTPApiRoleNotExist(role)

            return web.json_response(dict(id=result.id,
                                          bound_claims=json.loads(result.bound_claims),
                                          nomad_claims=json.loads(result.nomad_claims),
                                          )
                                     )

    async def delete(self):
        role = self.request.match_info.get('role_name', None)
        if role is None:
            raise HTTPApiRoleDataInvalid('role_name')

        query = select([JwtRole]).where(JwtRole.role == role)
        async with self.request.app['db'].connect() as conn:
            row: AsyncResultProxy = await conn.execute(query)

            result: RowProxy = await row.fetchone()
            if result is None:
                raise HTTPApiRoleNotExist(role)

            await conn.execute(
                delete(JwtRole).where(JwtRole.role == role)
            )

            return web.json_response(dict(success=True))
