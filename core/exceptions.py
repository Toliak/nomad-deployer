from aiohttp.web_exceptions import HTTPUnauthorized, HTTPBadRequest, HTTPUnsupportedMediaType


class HTTPApiAdminTokenInvalid(HTTPUnauthorized):
    def __init__(self):
        super().__init__(reason='Admin token is invalid')


class HTTPApiNomadClaimsValidationError(HTTPBadRequest):
    def __init__(self, key=None):
        if key:
            super().__init__(reason=f'nomad_claims validation error at key: {key}')
        else:
            super().__init__(reason=f'nomad_claims validation: undefined key')


class HTTPApiBoundClaimsValidationError(HTTPBadRequest):
    def __init__(self, key=None):
        if key:
            super().__init__(reason=f'bound_claims validation error at key: {key}')
        else:
            super().__init__(reason=f'bound_claims validation: undefined key')


class HTTPApiNomadClaimsCheckError(HTTPBadRequest):
    def __init__(self, key=None):
        if key:
            super().__init__(reason=f'Nomad check error at key: {key}')
        else:
            super().__init__(reason=f'Nomad check error at key')


class HTTPApiRoleAlreadyExists(HTTPBadRequest):
    def __init__(self, rolename):
        super().__init__(reason=f'Role "{rolename}" already exists')


class HTTPApiRoleNotExist(HTTPBadRequest):
    def __init__(self, rolename):
        super().__init__(reason=f'Role "{rolename}" does not exist')


class HTTPApiRoleDataInvalid(HTTPBadRequest):
    def __init__(self, key):
        super().__init__(reason=f'Role data key "{key}" is invalid')


class HTTPApiConfigAlreadyExists(HTTPBadRequest):
    def __init__(self, rolename):
        super().__init__(reason=f'Config "{rolename}" already exists')


class HTTPApiConfigNotExist(HTTPBadRequest):
    def __init__(self, rolename):
        super().__init__(reason=f'Config "{rolename}" does not exist')


class HTTPApiConfigDataInvalid(HTTPBadRequest):
    def __init__(self, key):
        super().__init__(reason=f'Config data key "{key}" is invalid')


class HTTPApiContentTypeInvalid(HTTPUnsupportedMediaType):
    def __init__(self):
        super().__init__(reason=f'Supports only "application/json" Content-Type')


class HTTPApiEmptyBody(HTTPBadRequest):
    def __init__(self):
        super().__init__(reason=f'Request has an empty body')
