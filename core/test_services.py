from core.exceptions import HTTPApiNomadClaimsValidationError, HTTPApiNomadClaimsCheckError
from core.services import NomadClaimsService


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
        Name='^gitlab$',
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
