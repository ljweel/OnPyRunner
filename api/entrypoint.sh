#!/bin/bash
set -e

echo "[INFO] Running database migrations..."
alembic -c /app/db/alembic.ini upgrade head
echo "[INFO] Migrations complete."

exec "$@"