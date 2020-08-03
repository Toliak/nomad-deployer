#! /bin/sh

export PYTHONPATH=$PWD

alembic upgrade head

coverage run --source=. --omit=venv/*/** -m pytest
coverage report -m --omit=venv/**,**/migrations/**,**/test_*,**/apps.py,**/asgi.py,**/wsgi.py,manage.py