#!/bin/bash
set -e

echo "Waiting for database..."
while ! pg_isready -h db -p 5432 -U postgres; do
  sleep 1
done

echo "Creating user..."
PGPASSWORD=postgres psql -h db -p 5432 -U postgres -d postgres -c "CREATE ROLE et WITH LOGIN PASSWORD 'fer';" 2>/dev/null || true

echo "Creating test database..."
PGPASSWORD=postgres psql -h db -p 5432 -U postgres -d postgres -c "CREATE DATABASE schedule_manager_test;" 2>/dev/null || true

echo "Granting permissions..."
PGPASSWORD=postgres psql -h db -p 5432 -U postgres -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE schedule_db TO et;"
PGPASSWORD=postgres psql -h db -p 5432 -U postgres -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE schedule_manager_test TO et;"

echo "Running migrations..."
uv run python /app/scripts/run_migrations.py

echo "Starting application..."
exec uv run uvicorn src.schedule_manager.main:app --host 0.0.0.0 --port 8000
