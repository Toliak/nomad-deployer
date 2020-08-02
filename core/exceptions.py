from aiohttp.web_exceptions import HTTPUnauthorized, HTTPBadRequest, HTTPUnsupportedMediaType, HTTPServiceUnavailable


class HTTPApiAdminTokenInvalid(HTTPUnauthorized):
    def __init__(self):
        super().__init__(reason='Admin token is invalid')


class HTTPApiNomadClaimsValidationError(HTTPBadRequest):
    def __init__(self, key=None):
        if key:
            super().__init__(reason=f'nomad_claims validation error at key: {key}')
        else:
            super().__init__(reason=f'nomad_claims validation: undefined')


class HTTPApiBoundClaimsValidationError(HTTPBadRequest):
    def __init__(self, key=None):
        if key:
            super().__init__(reason=f'bound_claims validation error at key: {key}')
        else:
            super().__init__(reason=f'bound_claims validation: undefined')


class HTTPApiNomadClaimsCheckError(HTTPBadRequest):
    def __init__(self, key=None):
        if key:
            super().__init__(reason=f'Nomad check error at key: {key}')
        else:
            super().__init__(reason=f'Nomad check error at key: undefined')


class HTTPApiBoundClaimsCheckError(HTTPBadRequest):
    def __init__(self, key=None):
        if key:
            super().__init__(reason=f'Bound claims check error at key: {key}')
        else:
            super().__init__(reason=f'Bound claims check error at key: undefined')


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


class HTTPApiNomadServiceTransformException(HTTPBadRequest):
    def __init__(self, message):
        super().__init__(reason=f'Transform error: {message}')


class HTTPApiNomadServiceRunException(HTTPBadRequest):
    def __init__(self, message):
        super().__init__(reason=f'Run error: {message}')


class HTTPApiConfigServiceJwksError(HTTPServiceUnavailable):
    def __init__(self, url):
        super().__init__(reason=f'Failed to retrieve JWKS from: {url}')


class HTTPApiConfigServiceJWTError(HTTPBadRequest):
    def __init__(self, url):
        super().__init__(reason=f'{url}')
