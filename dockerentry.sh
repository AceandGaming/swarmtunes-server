#!/bin/sh
set -e

# For use by docker. Avoid running manually!

case "$1" in
  migrate)
    echo "Running db migrations"
    uv run --no-sync alembic upgrade head
    ;;
  stamp)
    uv run --no-sync alembic stamp "$2"
    ;;
  debug)
    sleep infinity
    ;;
  *)
    echo "Running db migrations"
    uv run --no-sync alembic upgrade head

    echo "Starting server"
    exec uv run --no-sync uvicorn st.main:app --host 0.0.0.0 --port 8000
    ;;
esac