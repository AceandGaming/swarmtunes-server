#!/bin/sh
set -e

# For use by docker. Avoid running manually!

case "$1" in
  migrate)
    echo "Running db migrations"
    alembic upgrade head
    ;;
  stamp)
    alembic stamp "$2"
    ;;
  debug)
    sleep infinity
    ;;
  *)
    echo "Running db migrations"
    alembic upgrade head

    echo "Starting server"
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
    ;;
esac