import json

import pytest
from aiohttp.test_utils import TestClient
from sqlalchemy import insert

from core.app import create_app
# TODO: token to auth headers
from core.tables import JwtRole


@pytest.fixture
async def jwt_role(db, nomad_validator):
    async with db.connect() as conn:
        return await conn.execute(
            insert(JwtRole).values(dict(role='role-test',
                                        bound_claims='{"project_id":"1"}',
                                        nomad_claims=json.dumps(nomad_validator)))
        )


@pytest.fixture
async def headers():
    return {'Content-Type': 'application/json'}


@pytest.fixture
async def admin_headers(headers):
    headers['Authorization'] = 'Bearer admin_token_test'
    return headers


async def test_role_view_put_correct(aiohttp_client,
                                     prepare_db,
                                     admin_headers):
    """
    Expected: role name in url
    Expected data: token, bound_claims (json), nomad_claims (json)
    Should return 200

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.put('/role/role-test',
                            headers=admin_headers,
                            json=dict(
                                bound_claims='{"project_id":"1"}',
                                nomad_claims='{"Name":"^test-service$"}'))
    assert resp.status == 200
    text = await resp.text()
    assert '"id": 1' in text


async def test_role_view_put_exists(aiohttp_client,
                                    prepare_db,
                                    admin_headers,
                                    jwt_role):
    """
    Should raise 400

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.put('/role/role-test',
                            headers=admin_headers,
                            json=dict(bound_claims='{"project_id":"22"}',
                                      nomad_claims='{}'))
    assert resp.status == 400
    text = await resp.text()
    assert '"detail"' in text
    assert 'exist' in text


async def test_role_view_put_wrong_data_bound(aiohttp_client,
                                              admin_headers,
                                              prepare_db):
    """
    Should raise 400

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.put('/role/role-test',
                            headers=admin_headers,
                            json=dict(bound_claims='{"proje"""ct_id":"22"}',
                                      nomad_claims='{}'))
    assert resp.status == 400
    text = await resp.text()
    assert '"detail"' in text
    assert 'error' in text
    assert 'bound_claims' in text


async def test_role_view_put_wrong_data_nomad(aiohttp_client,
                                              admin_headers,
                                              prepare_db):
    """
    Should raise 400

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.put('/role/role-test',
                            headers=admin_headers,
                            json=dict(bound_claims='{}',
                                      nomad_claims='{"project_id":"22"}'))
    assert resp.status == 400
    text = await resp.text()
    assert '"detail"' in text
    assert 'error' in text
    assert 'nomad_claims' in text


async def test_role_view_put_wrong_token(aiohttp_client,
                                         admin_headers,
                                         prepare_db):
    """
    Should raise 401

    """
    client: TestClient = await aiohttp_client(create_app)
    admin_headers['Authorization'] = 'Bearer wrong-token'
    resp = await client.put('/role/role-test',
                            headers=admin_headers,
                            json=dict(bound_claims='{}',
                                      nomad_claims='{}'))
    assert resp.status == 401
    text = await resp.text()
    assert '"detail"' in text
    assert 'invalid' in text
    assert 'token' in text


async def test_role_view_get_correct(aiohttp_client,
                                     prepare_db,
                                     admin_headers,
                                     jwt_role):
    """
    Should return correct info

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.get('/role/role-test',
                            headers=admin_headers)
    assert resp.status == 200
    text = await resp.text()
    assert '"bound_claims"' in text
    assert '"nomad_claims"' in text
    assert '"id"' in text


async def test_role_view_get_wrong_token(aiohttp_client,
                                         prepare_db,
                                         admin_headers,
                                         jwt_role):
    """
    Should raise 401

    """
    client: TestClient = await aiohttp_client(create_app)
    admin_headers['Authorization'] = 'Bearer wrong-token'
    resp = await client.get('/role/role-test',
                            headers=admin_headers)
    assert resp.status == 401
    text = await resp.text()
    assert '"detail"' in text
    assert 'invalid' in text
    assert 'token' in text


async def test_role_view_get_not_found(aiohttp_client,
                                       prepare_db,
                                       admin_headers,
                                       jwt_role):
    """
    Should raise 400

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.get('/role/role-test-not-exist',
                            headers=admin_headers)
    assert resp.status == 400
    text = await resp.text()
    assert '"detail"' in text
    assert 'not exist' in text


async def test_role_view_delete_wrong_token(aiohttp_client,
                                            prepare_db,
                                            admin_headers,
                                            jwt_role):
    """
    Should raise 401

    """
    client: TestClient = await aiohttp_client(create_app)
    admin_headers['Authorization'] = 'Bearer wrong-token'
    resp = await client.delete('/role/role-test',
                               headers=admin_headers)
    assert resp.status == 401
    text = await resp.text()
    assert '"detail"' in text
    assert 'invalid' in text
    assert 'token' in text


async def test_role_view_delete_correct(aiohttp_client,
                                        prepare_db,
                                        admin_headers,
                                        jwt_role):
    """
    Should return 200

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.delete('/role/role-test',
                               headers=admin_headers)
    assert resp.status == 200
    text = await resp.text()
    assert '"success": true' in text


async def test_role_view_delete_not_exists(aiohttp_client,
                                           admin_headers,
                                           prepare_db):
    """
    Should raise 400

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.delete('/role/role-test',
                               headers=admin_headers)
    assert resp.status == 400
    text = await resp.text()
    assert '"detail"' in text
    assert 'not exist' in text


async def test_role_view_list_correct(aiohttp_client,
                                      prepare_db,
                                      admin_headers,
                                      jwt_role):
    """
    Should return correct info

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.get('/role/?list',
                            headers=admin_headers)
    assert resp.status == 200
    text = await resp.text()
    assert '"id": 1' in text
    assert '"role": "role-test"' in text


async def test_role_view_list_wrong_token(aiohttp_client,
                                          prepare_db,
                                          admin_headers,
                                          jwt_role):
    """
    Should raise 401

    """
    client: TestClient = await aiohttp_client(create_app)
    admin_headers['Authorization'] = 'Bearer wrong-token'
    resp = await client.get('/role/?list',
                            headers=admin_headers)
    assert resp.status == 401
    text = await resp.text()
    assert '"detail"' in text
    assert 'invalid' in text
    assert 'token' in text
