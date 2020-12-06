import json

import pytest
from aiohttp.web_exceptions import HTTPBadRequest
from nomad.api.exceptions import BadRequestNomadException

from core.exceptions import HTTPApiNomadClaimsValidationError, HTTPApiNomadClaimsCheckError, \
    HTTPApiBoundClaimsCheckError
from core.services import NomadClaimsService, NomadService, ConfigService, BoundClaimsService


def test_nomad_claims_service_validate_few_fields():
    structure = dict(
        Name='some-name',
        Type='some-type',
    )

    assert NomadClaimsService.validate(structure) is True


def test_nomad_claims_service_validate_few_fields_unexpected():
    structure = dict(
        Name='some-name',
        Type='some-type',
        Unknown='some-value-here'
    )

    try:
        NomadClaimsService.validate(structure)
        assert False
    except HTTPApiNomadClaimsValidationError:
        assert True


def test_nomad_claims_service_validate_with_list():
    structure = dict(
        Name='some-name',
        Type='some-type',
        TaskGroups=[dict()],
    )

    assert NomadClaimsService.validate(structure) is True


def test_nomad_claims_service_validate_with_list_multiple_fail():
    structure = dict(
        Name='some-name',
        Type='some-type',
        TaskGroups=[dict(), dict()],
    )

    try:
        NomadClaimsService.validate(structure)
        assert False
    except HTTPApiNomadClaimsValidationError:
        assert True


def test_nomad_claims_service_validate_full():
    structure = dict(
        Name='regex',
        Type='str',
        TaskGroups=[dict(
            Name='str',
            Tasks=[dict(
                Name='regex',
                Driver='str',
                User='str',
                Config=dict(
                    network_mode='str',
                    image='regex',
                    network_aliases=['str'],
                    port_map=[dict()],
                    volumes=['regex'],
                ),
                Vault=dict()
            )]
        )]
    )

    assert NomadClaimsService.validate(structure) is True


def test_nomad_claims_service_validate_full_fail_error_check():
    structure = dict(
        Name='regex',
        Type='str',
        TaskGroups=[dict(
            Name='str',
            Tasks=[dict(
                Name='regex',
                Driver='str',
                User='str',
                Config=dict(
                    network_mode='str',
                    image='regex',
                    network_aliases=['str'],
                    port_map=[dict()],
                    volumes=['regex', 'fail'],
                ),
                Vault=dict(
                    Policies=['str'],
                )
            )]
        )]
    )

    try:
        NomadClaimsService.validate(structure)
        assert False
    except HTTPApiNomadClaimsValidationError as e:
        assert 'ROOT.TaskGroups.0.Tasks.0.Config.volumes' in str(e)


def test_nomad_claims_service_check_nomad_config_few_fields(nomad_config_json):
    structure = dict(
        Name='^test-deployer$',
        Type='service',
    )

    assert NomadClaimsService.check_nomad_config(nomad_config_json, structure) is True


def test_nomad_claims_service_check_nomad_config_fail_regex(nomad_config_json):
    structure = dict(
        Name='^gitl$',
        Type='service',
    )

    try:
        NomadClaimsService.check_nomad_config(nomad_config_json, structure)
        assert False
    except HTTPApiNomadClaimsCheckError as e:
        assert 'ROOT.Name' in str(e)


def test_nomad_claims_service_check_nomad_config_full_correct(nomad_config_json,
                                                              nomad_validator):
    assert NomadClaimsService.check_nomad_config(nomad_config_json, nomad_validator) is True


def test_nomad_service_transform_correct(mocker,
                                         nomad_hcl_job,
                                         nomad_config_json):
    def mock_function(*args, **kwargs):
        mock_function.called = True
        return nomad_config_json

    mock_function.called = False

    mocker.patch('nomad.api.jobs.Jobs.parse', new=mock_function)
    response = NomadService.transform(nomad_hcl_job)

    assert mock_function.called is True
    assert type(response) == dict


def test_nomad_service_transform_fail(mocker,
                                      nomad_hcl_job,
                                      nomad_config_json):
    def mock_function(*args, **kwargs):
        mock_function.called = True
        raise BadRequestNomadException('something went wrong')

    mock_function.called = False

    mocker.patch('nomad.api.jobs.Jobs.parse', new=mock_function)
    try:
        NomadService.transform("""hey hello it's not hcl it's plain text ok""")
        assert False
    except HTTPBadRequest:
        assert True

    assert mock_function.called is True


def test_nomad_service_run_correct(mocker,
                                   nomad_config_json):
    def mock_function(*args, **kwargs):
        mock_function.called = True
        return json.loads('''{
    "EvalID": "d1b4fc54-bf68-0a54-94ee-4460f41a13ba",
    "EvalCreateIndex": 62498,
    "JobModifyIndex": 62498,
    "Warnings": "",
    "Index": 62498,
    "LastContact": 0,
    "KnownLeader": false
}''')

    mock_function.called = False

    mocker.patch('core.services.NomadService.nomad_host.job.register_job', new=mock_function)
    response = NomadService.run(nomad_config_json)

    assert mock_function.called is True
    assert type(response) == dict


def test_nomad_service_run_fail(mocker,
                                nomad_hcl_job,
                                nomad_config_json):
    def mock_function(*args, **kwargs):
        mock_function.called = True
        raise BadRequestNomadException('something went wrong')

    mock_function.called = False

    mocker.patch('core.services.NomadService.nomad_host.job.register_job', new=mock_function)
    try:
        NomadService.run(dict(Name="""hey hello it's not hcl it's plain text ok"""))
        assert False
    except HTTPBadRequest:
        assert True

    assert mock_function.called is True


def test_config_service_get_issuer(ci_job_jwt):
    issuer = ConfigService.get_issuer(ci_job_jwt)
    assert issuer == 'gitlab.toliak.ru'


async def test_config_service_get_jwks():
    keys = await ConfigService.get_jwks('https://gitlab.com/-/jwks')
    assert type(keys) == dict
    assert type(keys.get('keys')) == list
    assert type(keys.get('keys')[0].get('n')) == str


async def test_config_service_validate_correct(ci_job_jwt,
                                               jwks_response):
    try:
        response = await ConfigService.validate(ci_job_jwt, json.loads(jwks_response))
        assert False
    except HTTPBadRequest as e:
        assert True
        assert 'expired' in str(e)


async def test_config_service_validate_fail(ci_job_jwt,
                                            jwks_response):
    ci_job_jwt = ci_job_jwt[:-1]
    try:
        response = await ConfigService.validate(ci_job_jwt, json.loads(jwks_response))
        assert False
    except HTTPBadRequest as e:
        assert True
        assert 'failed' in str(e)


async def test_bound_claims_service_check_jwt_correct(ci_job_jwt_body):
    body = json.loads(ci_job_jwt_body)
    validator = dict(project_id='76',
                     ref='some-branch')
    response = BoundClaimsService.check_jwt(body, validator)

    assert response is True


async def test_bound_claims_service_check_jwt_fail(ci_job_jwt_body):
    body = json.loads(ci_job_jwt_body)
    validator = dict(project_id='76',
                     ref='some-wrong-branch')
    try:
        BoundClaimsService.check_jwt(body, validator)
        assert False
    except HTTPApiBoundClaimsCheckError as e:
        assert True
        assert 'ROOT.ref' in str(e)


async def test_bound_claims_service_check_jwt_fail_new_key(ci_job_jwt_body):
    body = json.loads(ci_job_jwt_body)
    validator = dict(project_id='76',
                     expected_key='some-value')
    try:
        BoundClaimsService.check_jwt(body, validator)
        assert False
    except HTTPApiBoundClaimsCheckError as e:
        assert True
        assert 'ROOT.expected_key' in str(e)


def test_nomad_claims_service_check_nomad_config_constraint_fail(nomad_config_json,
                                                                 nomad_validator):
    nomad_config_json['Constraints'][0]['RTarget'] = 'e_prod'

    with pytest.raises(HTTPApiNomadClaimsCheckError) as e:
        NomadClaimsService.check_nomad_config(nomad_config_json, nomad_validator)

    assert 'ROOT.Constraints.0.RTarget' in str(e)


def test_nomad_claims_service_check_nomad_config_constraint_double(nomad_config_json,
                                                                   nomad_validator):
    nomad_config_json['Constraints'].append(dict(
        LTarget=r'^.+client_id\}$',
        RTarget='^prod$',
        Operand='=',
    ))

    with pytest.raises(HTTPApiNomadClaimsCheckError) as e:
        NomadClaimsService.check_nomad_config(nomad_config_json, nomad_validator)

    assert 'ROOT.Constraints.1.LTarget' in str(e)
