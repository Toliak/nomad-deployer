from aiohttp.web_exceptions import HTTPBadRequest


class HTTPApiAdminTokenInvalid(HTTPBadRequest):
    def __init__(self):
        super().__init__(reason='Admin token is invalid')
