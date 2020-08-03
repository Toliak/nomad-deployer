#! /bin/sh

export PYTHONPATH=$PWD

alembic upgrade head

exec coverage run --source=. --omit=venv/*/** -m pytest