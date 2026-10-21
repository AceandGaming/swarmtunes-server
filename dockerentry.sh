#!/bin/sh
set -e

# For use by docker. Avoid running manually!

case "$1" in
  migrate)
    echo "Running db migrations"
    uv run alembic upgrade head
    ;;
  stamp)
    uv run alembic stamp "$2"
    ;;
  debug)
    sleep infinity
    ;;
  *)
    echo "Running db migrations"
    uv run alembic upgrade head

    echo "Starting server"
    exec uv run uvicorn st.main:app --host 0.0.0.0 --port 8000
    ;;
esac