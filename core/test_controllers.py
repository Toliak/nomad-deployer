import json

import cryptography.hazmat.backends
import pytest
from aiohttp.test_utils import TestClient
from jwt import PyJWT
from sqlalchemy import insert

from core.app import create_app
from core.tables import JwtRole, JwtConfig


@pytest.fixture
async def jwt_role(db, nomad_validator):
    async with db.connect() as conn:
        return await conn.execute(
            insert(JwtRole).values(dict(role='role-test',
                                        bound_claims='{"project_id":"76"}',
                                        nomad_claims=json.dumps(nomad_validator)))
        )


@pytest.fixture
async def jwt_config(db):
    async with db.connect() as conn:
        return await conn.execute(
            insert(JwtConfig).values(dict(jwks_url='https://gitlab.toliak.ru/-/jwks',
                                          bound_issuer='gitlab.toliak.ru', ))
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


async def test_config_view_put_correct(aiohttp_client,
                                       prepare_db,
                                       admin_headers):
    """
    Expected data: jwks_url, bound_issuer
    Should return 200
    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.put('/config/',
                            headers=admin_headers,
                            json=dict(jwks_url='https://gitlab.toliak.ru/-/jwks',
                                      bound_issuer='gitlab.toliak.ru'))
    assert resp.status == 200
    text = await resp.text()
    assert '"id": 1' in text


async def test_config_view_put_exists(aiohttp_client,
                                      prepare_db,
                                      admin_headers,
                                      jwt_config):
    """
    Should raise 400
    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.put('/config/',
                            headers=admin_headers,
                            json=dict(jwks_url='https://gitlab.toliak.ru/-/jwks',
                                      bound_issuer='gitlab.toliak.ru'))
    assert resp.status == 400
    text = await resp.text()
    assert '"detail"' in text
    assert 'exist' in text


async def test_config_view_put_wrong_data_jwks(aiohttp_client,
                                               admin_headers,
                                               prepare_db):
    """
    Should raise 400
    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.put('/config/',
                            headers=admin_headers,
                            json=dict(bound_issuer='gitlab.toliak.ru'))
    assert resp.status == 400
    text = await resp.text()
    assert '"detail"' in text
    assert 'invalid' in text
    assert 'jwks_url' in text


async def test_config_view_put_wrong_data_bound(aiohttp_client,
                                                admin_headers,
                                                prepare_db):
    """
    Should raise 400
    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.put('/config/',
                            headers=admin_headers,
                            json=dict(jwks_url='https://gitlab.toliak.ru/-/jwks'))
    assert resp.status == 400
    text = await resp.text()
    assert '"detail"' in text
    assert 'invalid' in text
    assert 'bound_issuer' in text


async def test_config_view_put_wrong_token(aiohttp_client,
                                           admin_headers,
                                           prepare_db):
    """
    Should raise 401
    """
    client: TestClient = await aiohttp_client(create_app)
    admin_headers['Authorization'] = 'Bearer wrong-token'
    resp = await client.put('/config/',
                            headers=admin_headers,
                            json=dict(jwks_url='https://gitlab.toliak.ru/-/jwks',
                                      bound_issuer='gitlab.toliak.ru'))
    assert resp.status == 401
    text = await resp.text()
    assert '"detail"' in text
    assert 'invalid' in text
    assert 'token' in text


async def test_config_view_get_correct(aiohttp_client,
                                       prepare_db,
                                       admin_headers,
                                       jwt_config):
    """
    Should return correct info
    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.get('/config/?bound_issuer=gitlab.toliak.ru',
                            headers=admin_headers)
    assert resp.status == 200
    text = await resp.text()
    assert '"jwks_url"' in text
    assert '"bound_issuer"' in text
    assert '"id"' in text


async def test_config_view_get_wrong_token(aiohttp_client,
                                           prepare_db,
                                           admin_headers,
                                           jwt_config):
    """
    Should raise 401
    """
    client: TestClient = await aiohttp_client(create_app)
    admin_headers['Authorization'] = 'Bearer wrong-token'
    resp = await client.get('/config/?bound_issuer=gitlab.toliak.ru',
                            headers=admin_headers)
    assert resp.status == 401
    text = await resp.text()
    assert '"detail"' in text
    assert 'invalid' in text
    assert 'token' in text


async def test_config_view_get_not_found(aiohttp_client,
                                         prepare_db,
                                         admin_headers,
                                         jwt_config):
    """
    Should raise 400
    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.get('/config/?bound_issuer=unknown',
                            headers=admin_headers)
    assert resp.status == 400
    text = await resp.text()
    assert '"detail"' in text
    assert 'not exist' in text


async def test_config_view_delete_wrong_token(aiohttp_client,
                                              prepare_db,
                                              admin_headers,
                                              jwt_config):
    """
    Should raise 401
    """
    client: TestClient = await aiohttp_client(create_app)
    admin_headers['Authorization'] = 'Bearer wrong-token'
    resp = await client.delete('/config/',
                               headers=admin_headers,
                               json=dict(bound_issuer='gitlab.toliak.ru'))
    assert resp.status == 401
    text = await resp.text()
    assert '"detail"' in text
    assert 'invalid' in text
    assert 'token' in text


async def test_config_view_delete_correct(aiohttp_client,
                                          prepare_db,
                                          admin_headers,
                                          jwt_config):
    """
    Should return 200

    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.delete('/config/',
                               headers=admin_headers,
                               json=dict(bound_issuer='gitlab.toliak.ru'))
    assert resp.status == 200
    text = await resp.text()
    assert '"success": true' in text


async def test_config_view_delete_empty_request(aiohttp_client,
                                                prepare_db,
                                                admin_headers,
                                                jwt_config):
    """
    Should return 415
    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.delete('/config/',
                               headers=admin_headers)
    assert resp.status == 400
    text = await resp.text()
    assert 'empty' in text.lower()


async def test_config_view_delete_wrong_content_type(aiohttp_client,
                                                     prepare_db,
                                                     admin_headers,
                                                     jwt_config):
    """
    Should return 415
    """
    client: TestClient = await aiohttp_client(create_app)
    admin_headers['Content-Type'] = 'application/xml'
    resp = await client.delete('/config/',
                               headers=admin_headers)
    assert resp.status == 415
    text = await resp.text()
    assert 'support' in text.lower()


async def test_config_view_delete_not_exists(aiohttp_client,
                                             admin_headers,
                                             prepare_db):
    """
    Should raise 400
    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.delete('/config/',
                               headers=admin_headers,
                               json=dict(bound_issuer='gitlab.toliak.ru'))
    assert resp.status == 400
    text = await resp.text()
    assert '"detail"' in text
    assert 'not exist' in text


async def test_config_view_list_correct(aiohttp_client,
                                        prepare_db,
                                        admin_headers,
                                        jwt_config):
    """
    Should return correct info
    """
    client: TestClient = await aiohttp_client(create_app)
    resp = await client.get('/config/?list',
                            headers=admin_headers)
    assert resp.status == 200
    text = await resp.text()
    assert '"id": 1' in text
    assert '"bound_issuer": "gitlab.toliak.ru"' in text


async def test_config_view_list_wrong_token(aiohttp_client,
                                            prepare_db,
                                            admin_headers,
                                            jwt_config):
    """
    Should raise 401
    """
    client: TestClient = await aiohttp_client(create_app)
    admin_headers['Authorization'] = 'Bearer wrong-token'
    resp = await client.get('/config/?list',
                            headers=admin_headers)
    assert resp.status == 401
    text = await resp.text()
    assert '"detail"' in text
    assert 'invalid' in text
    assert 'token' in text


@pytest.fixture
def run_view_post_mock_everything(mocker,
                                  nomad_hcl_job,
                                  ci_job_jwt,
                                  jwks_response,
                                  ci_job_jwt_body,
                                  nomad_config_json):
    async def mock_get_jwks(jwks_url):
        assert jwks_url == 'https://gitlab.toliak.ru/-/jwks'
        mock_get_jwks.called = True
        return json.loads(jwks_response)

    mock_get_jwks.called = False

    def mock_jwt_decode(encoded, key=None, algorithms=None, verify=True):
        if verify is True:
            assert type(algorithms) == list
            assert isinstance(key, cryptography.hazmat.backends.openssl.rsa._RSAPublicKey)
            assert encoded == ci_job_jwt
            mock_jwt_decode.called = True

            return json.loads(ci_job_jwt_body)

        return PyJWT().decode(encoded, verify=False)

    mock_jwt_decode.called = False

    def mock_nomad_transform(hcl):
        assert hcl == nomad_hcl_job
        mock_nomad_transform.called = True

        return nomad_config_json

    mock_nomad_transform.called = False

    def mock_nomad_register_job(this, uid, job):
        assert uid == 'test-deployer'
        assert type(job) == dict
        mock_nomad_register_job.called = True

        return dict(ok=True)

    mock_nomad_register_job.called = False

    mocker.patch('core.services.ConfigService.get_jwks', new=mock_get_jwks)
    mocker.patch('jwt.decode', new=mock_jwt_decode)
    mocker.patch('core.services.NomadService.transform', new=mock_nomad_transform)
    mocker.patch('nomad.api.job.Job.register_job', new=mock_nomad_register_job)

    return [mock_get_jwks,
            mock_jwt_decode,
            mock_nomad_transform,
            mock_nomad_register_job, ]


async def test_run_view_post_correct(aiohttp_client,
                                     prepare_db,
                                     headers,
                                     jwt_role,
                                     jwt_config,
                                     nomad_hcl_job,
                                     ci_job_jwt,
                                     run_view_post_mock_everything):
    """
    Expected: job_hcl, role, jwt
    Should return 200
    """
    [mock_get_jwks,
     mock_jwt_decode,
     mock_nomad_transform,
     mock_nomad_register_job, ] = run_view_post_mock_everything

    client: TestClient = await aiohttp_client(create_app)
    response = await client.post('/run/',
                                 headers=headers,
                                 json=dict(job_hcl=nomad_hcl_job,
                                           role='role-test',
                                           jwt=ci_job_jwt))
    assert response.status == 200
    text = await response.text()
    assert '"success": true' in text

    assert mock_get_jwks.called is True
    assert mock_jwt_decode.called is True
    assert mock_nomad_transform.called is True
    assert mock_nomad_register_job.called is True
