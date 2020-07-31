import os


def get_env(key):
    result = os.environ.get(key, None)
    if result is None:
        raise RuntimeError(f'Environment variable "{key}" is unset')

    return result


connection_uri = get_env('SQLALCHEMY_URI')
connection_params = dict(uri=get_env('SQLALCHEMY_URI'), echo=True)
admin_token = get_env('ADMIN_TOKEN')

if len(admin_token) < 8:
    raise RuntimeError(f'Expected "admin_token" to be at least 8 char len')
