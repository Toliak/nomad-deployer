from aiohttp.test_utils import TestClient

from core.app import create_app


# TODO: token to auth headers

async def test_role_view_put_correct(aiohttp_client):
    """
    Expected: role name in url
    Expected data: token, bound_claims (json), nomad_claims (json)

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.post('/role/role-test',
                             data=dict(token='admin_token_test',
                                       bound_claims='{"project_id":"22"}',
                                       nomad_claims='{}'))
    assert resp.status == 200
    text = await resp.text()
    assert '"id": 1' in text


async def test_role_view_put_exists(aiohttp_client):
    """
    Expected: role name in url
    Expected data: token, bound_claims (json), nomad_claims (json)

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.post('/role/role-test',
                             data=dict(token='admin_token_test',
                                       bound_claims='{"project_id":"22"}',
                                       nomad_claims='{}'))
    assert resp.status == 400
    text = await resp.text()
    assert '"detail"' in text
    assert 'exist' in text


async def test_role_view_put_wrong_data_bound(aiohttp_client):
    """
    Expected: role name in url
    Expected data: token, bound_claims (json), nomad_claims (json)

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.post('/role/role-test',
                             data=dict(token='admin_token_test',
                                       bound_claims='{"p"""""roject_id":"22"}',
                                       nomad_claims='{}'))
    assert resp.status == 400
    text = await resp.text()
    assert '"detail"' in text
    assert 'wrong' in text
    assert 'bound_claims' in text


async def test_role_view_put_wrong_data_nomad(aiohttp_client):
    """
    Expected: role name in url
    Expected data: token, bound_claims (json), nomad_claims (json)

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.post('/role/role-test',
                             data=dict(token='admin_token_test',
                                       bound_claims='{}',
                                       nomad_claims='{"p"""""roject_id":"22"}'))
    assert resp.status == 400
    text = await resp.text()
    assert '"detail"' in text
    assert 'wrong' in text
    assert 'nomad_claims' in text


async def test_role_view_put_wrong_token(aiohttp_client):
    """
    Expected: role name in url
    Expected data: token, bound_claims (json), nomad_claims (json)

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.post('/role/role-test',
                             data=dict(token='wrong-token',
                                       bound_claims='{}',
                                       nomad_claims='{}'))
    assert resp.status == 400
    text = await resp.text()
    assert '"detail"' in text
    assert 'wrong' in text
    assert 'nomad_claims' in text


async def test_role_view_get_correct(aiohttp_client):
    """
    Should return correct info

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.delete('/role/role-test',
                               data=dict(token='admin_token_test'))
    assert resp.status == 200
    text = await resp.text()
    assert '"detail"' in text
    assert 'wrong' in text
    assert 'nomad_claims' in text


async def test_role_view_get_wrong_token(aiohttp_client):
    """
    Should return correct info

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.delete('/role/role-test',
                               data=dict(token='admin_token_test'))
    assert resp.status == 200
    text = await resp.text()
    assert '"detail"' in text
    assert 'wrong' in text
    assert 'nomad_claims' in text


async def test_role_view_delete_wrong_token(aiohttp_client):
    """
    Should raise 400

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.delete('/role/role-test',
                               data=dict(token='wrong-token'))
    assert resp.status == 400
    text = await resp.text()
    assert '"detail"' in text
    assert 'wrong' in text
    assert 'nomad_claims' in text


async def test_role_view_delete_correct(aiohttp_client):
    """
    Should raise 200

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.delete('/role/role-test',
                               data=dict(token='admin_token_test'))
    assert resp.status == 200
    text = await resp.text()
    assert '"detail"' in text
    assert 'wrong' in text
    assert 'nomad_claims' in text


async def test_role_view_delete_not_exists(aiohttp_client):
    """
    Should raise 400

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.delete('/role/role-test',
                               data=dict(token='admin_token_test'))
    assert resp.status == 200
    text = await resp.text()
    assert '"detail"' in text
    assert 'wrong' in text
    assert 'nomad_claims' in text


async def test_role_view_list_wrong_token(aiohttp_client):
    """
    Should raise 401

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.get('/role/?list',
                               data=dict(token='admin_token_test'))
    assert resp.status == 200
    text = await resp.text()
    assert '"detail"' in text
    assert 'wrong' in text
    assert 'nomad_claims' in text


async def test_role_view_list_correct(aiohttp_client):
    """
    Should raise 200

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.delete('/role/role-test',
                               data=dict(token='admin_token_test'))
    assert resp.status == 200
    text = await resp.text()
    assert '"detail"' in text
    assert 'wrong' in text
    assert 'nomad_claims' in text
