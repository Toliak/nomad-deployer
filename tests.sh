#! /bin/sh

export SQLALCHEMY_URI=sqlite:///db_test.sqlite
export ADMIN_TOKEN=admin_token_test
export PYTHONPATH=$PWD

rm -f db_test.sqlite

alembic upgrade head

exec pytest