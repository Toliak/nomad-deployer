import json

from aiohttp import web


class ApiException(RuntimeError):
    def __init__(self, message, code, info=None):
        super().__init__(message)

        self.message = message
        self.code = code
        self.info = info

    def to_json(self):
        return json.dumps(dict(
            message=self.message,
            detail=self.info,
        ))

    def to_response(self):
        return web.Response(text=self.to_json(),
                            status=self.code)


def response_internal_error(exception):
    return web.Response(text=json.dumps(dict(message=str(exception),
                                             )),
                        status=500)


class MethodNotAllowedApiException(ApiException):
    def __init__(self, method):
        super().__init__(f"Method {method} not allowed", 405)
