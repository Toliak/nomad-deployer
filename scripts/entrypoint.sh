#! /bin/sh

export PYTHONPATH=/app/

./scripts/migrate.sh

exec python core/app.py