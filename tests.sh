#! /bin/sh

export PYTHONPATH=$PWD

alembic upgrade head

exec pytest