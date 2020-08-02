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
    HTTPApiRoleNotExist, HTTPApiBoundClaimsValidationError, HTTPApiNomadClaimsValidationError, HTTPApiConfigDataInvalid, \
    HTTPApiConfigAlreadyExists, HTTPApiConfigNotExist, HTTPApiContentTypeInvalid, HTTPApiEmptyBody
from core.services import BoundClaimsService, NomadClaimsService
from core.tables import JwtRole, JwtConfig


class JsonView(View):
    async def _iter(self):
        expected_content_type = 'application/json'
        content_type = self.request.content_type
        if content_type != expected_content_type:
            raise HTTPApiContentTypeInvalid()

        return await super()._iter()


class AdminView(JsonView):
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
        if self.request.can_read_body is False:
            raise HTTPApiEmptyBody()
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


class ConfigView(AdminView):
    async def put(self):
        if self.request.can_read_body is False:
            raise HTTPApiEmptyBody()
        data = await self.request.json()

        jwks_url = data.get('jwks_url', None)
        if jwks_url is None:
            raise HTTPApiConfigDataInvalid('jwks_url')
        bound_issuer = data.get('bound_issuer', None)
        if bound_issuer is None:
            raise HTTPApiConfigDataInvalid('bound_issuer')

        query = select([JwtConfig]).where(JwtConfig.bound_issuer == bound_issuer)
        async with self.request.app['db'].connect() as conn:
            row: AsyncResultProxy = await conn.execute(query)

            result: RowProxy = await row.fetchone()
            if result is not None:
                raise HTTPApiConfigAlreadyExists(bound_issuer)

            result: AsyncResultProxy = await conn.execute(
                insert(JwtConfig).values(dict(jwks_url=jwks_url,
                                              bound_issuer=bound_issuer))
            )
            return web.json_response(dict(id=result.inserted_primary_key[0], ))

    async def get_list(self):
        query = select([JwtConfig]).limit(1000)
        async with self.request.app['db'].connect() as conn:
            row: AsyncResultProxy = await conn.execute(query)
            result: RowProxy = await row.fetchall()

            response_list = [dict(id=value.id,
                                  bound_issuer=value.bound_issuer) for value in result]

            return web.json_response(response_list)

    async def get(self):
        if self.request.query.get('list') is not None:
            return await self.get_list()

        bound_issuer = self.request.query.get('bound_issuer')
        if bound_issuer is None:
            raise HTTPApiConfigDataInvalid('bound_issuer')

        query = select([JwtConfig]).where(JwtConfig.bound_issuer == bound_issuer)
        async with self.request.app['db'].connect() as conn:
            row: AsyncResultProxy = await conn.execute(query)

            result: RowProxy = await row.fetchone()
            if result is None:
                raise HTTPApiConfigNotExist(JwtConfig)

            return web.json_response(dict(id=result.id,
                                          bound_issuer=result.bound_issuer,
                                          jwks_url=result.jwks_url, ))

    async def delete(self):
        if self.request.can_read_body is False:
            raise HTTPApiEmptyBody()
        data = await self.request.json()

        bound_issuer = data.get('bound_issuer', None)
        if bound_issuer is None:
            raise HTTPApiConfigDataInvalid('bound_issuer')

        query = select([JwtConfig]).where(JwtConfig.bound_issuer == bound_issuer)
        async with self.request.app['db'].connect() as conn:
            row: AsyncResultProxy = await conn.execute(query)

            result: RowProxy = await row.fetchone()
            if result is None:
                raise HTTPApiConfigNotExist(bound_issuer)

            await conn.execute(
                delete(JwtConfig).where(JwtConfig.bound_issuer == bound_issuer)
            )

            return web.json_response(dict(success=True))
