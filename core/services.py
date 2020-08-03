import json
import re

import aiohttp
import jwt
import jwt.algorithms
import nomad
from jwt import PyJWTError

from core.exceptions import HTTPApiNomadClaimsValidationError, HTTPApiNomadClaimsCheckError, \
    HTTPApiBoundClaimsValidationError, HTTPApiNomadServiceTransformException, HTTPApiNomadServiceRunException, \
    HTTPApiConfigServiceJWTError, HTTPApiBoundClaimsCheckError


class BoundClaimsService:
    @staticmethod
    def validate(data):
        if type(data) != dict:
            raise HTTPApiBoundClaimsValidationError('ROOT')

        return True

    @staticmethod
    def _check_jwt_internal(config, validator, origin_key):
        if type(validator) == dict:
            for key in validator:
                value = config.get(key, None)
                if value is None:
                    raise HTTPApiBoundClaimsCheckError(f'{origin_key}.{key}')

                validator_value = validator[key]
                if type(validator_value) == str or type(validator_value) == int:
                    if validator_value != value:
                        raise HTTPApiBoundClaimsCheckError(f'{origin_key}.{key}')
                else:
                    raise HTTPApiBoundClaimsCheckError(f'{origin_key}.{key}')

    @staticmethod
    def check_jwt(config, validator):
        BoundClaimsService._check_jwt_internal(config, validator, 'ROOT')
        return True


class NomadClaimsService:
    nomad_claims_structure = dict(
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
                Vault=dict(
                    Policies=['str']
                )
            )]
        )]
    )

    @staticmethod
    def _validate_internal(data, structure, origin_key):
        length = len(data)

        if type(structure) == dict:
            if type(data) != dict:
                raise HTTPApiNomadClaimsValidationError(f'{origin_key}')

            for key in structure:
                value = data.get(key, None)
                if value is None:
                    continue

                if isinstance(value, type(structure[key])):
                    length -= 1

                    if type(structure[key]) == list or type(structure[key]) == dict:
                        NomadClaimsService._validate_internal(value, structure[key], f'{origin_key}.{key}')

                    continue
                raise HTTPApiNomadClaimsValidationError(f'{origin_key}.{key}')

            if length > 0:
                raise HTTPApiNomadClaimsValidationError(f'{origin_key}')

        if type(structure) == list:
            if type(data) != list or len(data) > 1:
                raise HTTPApiNomadClaimsValidationError(f'{origin_key}')

            if len(structure) == 0:
                return

            if type(structure[0]) == list or (type(structure[0]) == dict and len(structure[0]) > 0):
                for i, value in enumerate(data):
                    NomadClaimsService._validate_internal(value, structure[0], f'{origin_key}.{i}')
                return

            for i, value in enumerate(data):
                if not isinstance(value, type(structure[0])):
                    raise HTTPApiNomadClaimsValidationError(f'{origin_key}.{i}')

    @staticmethod
    def validate(data):
        if type(data) != dict:
            raise HTTPApiNomadClaimsValidationError('ROOT')

        NomadClaimsService._validate_internal(data,
                                              NomadClaimsService.nomad_claims_structure,
                                              'ROOT')
        return True

    @staticmethod
    def _check_nomad_config_internal_partial(config_value, validator_value, origin_key):
        if type(validator_value) == list or (type(validator_value) == dict and len(validator_value) > 0):
            NomadClaimsService._check_nomad_config_internal(config_value, validator_value, origin_key)
            return

        if type(validator_value) == str:
            if not re.match(validator_value, config_value):
                raise HTTPApiNomadClaimsCheckError(origin_key)
        elif type(validator_value) == int:
            if validator_value != config_value:
                raise HTTPApiNomadClaimsCheckError(origin_key)

    @staticmethod
    def _check_nomad_config_internal(config, validator, origin_key):
        if type(validator) == dict:
            for key in validator:
                value = config.get(key, None)
                if value is None:
                    continue

                validator_value = validator[key]
                NomadClaimsService._check_nomad_config_internal_partial(value, validator_value, f'{origin_key}.{key}')

        if type(validator) == list:
            if len(validator) == 0:
                return

            validator_value = validator[0]
            for i, value in enumerate(config):
                NomadClaimsService._check_nomad_config_internal_partial(value, validator_value, f'{origin_key}.{i}')

    @staticmethod
    def check_nomad_config(config, validator):
        NomadClaimsService._check_nomad_config_internal(config, validator, 'ROOT')
        return True


class ConfigService:
    @staticmethod
    def get_issuer(encoded):
        data = jwt.decode(encoded, verify=False)
        return data.get('iss')

    @staticmethod
    async def get_jwks(url) -> dict:
        async with aiohttp.ClientSession() as client:
            async with client.get(url) as resp:
                assert resp.status == 200
                response = await resp.text()
                keys = json.loads(response)

                return keys

    # https://renzolucioni.com/verifying-jwts-with-jwks-and-pyjwt/
    @staticmethod
    def validate(encoded, jwks):
        public_keys = dict()
        for jwk in jwks['keys']:
            kid = jwk['kid']
            public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

        kid = jwt.get_unverified_header(encoded)['kid']
        key = public_keys[kid]

        try:
            payload = jwt.decode(encoded, key=key, algorithms=['RS256'])
        except PyJWTError as e:
            raise HTTPApiConfigServiceJWTError(f'JWT Decode error: {str(e)}')

        return payload


class NomadService:
    nomad_host = nomad.Nomad()

    @staticmethod
    def transform(hcl_job) -> dict:
        try:
            return NomadService.nomad_host.jobs.parse(hcl_job)
        except nomad.api.exceptions.BaseNomadException as e:
            raise HTTPApiNomadServiceTransformException(
                e.nomad_resp.text if hasattr(e.nomad_resp, "text") else str(e.nomad_resp))

    @staticmethod
    def run(job_data: dict):
        data = dict(Job=job_data)

        try:
            name = job_data['Name']
            return NomadService.nomad_host.job.register_job(name, data)
        except nomad.api.exceptions.BaseNomadException as e:
            raise HTTPApiNomadServiceRunException(
                e.nomad_resp.text if hasattr(e.nomad_resp, "text") else str(e.nomad_resp))
        except KeyError:
            raise HTTPApiNomadServiceRunException('Name key not found')
