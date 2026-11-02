#!/usr/bin/env bash
set -e

if [ -n "$POSTGRES_TEST_DB" ]; then
    echo "Creating test database: $POSTGRES_TEST_DB"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
        SELECT 'CREATE DATABASE "$POSTGRES_TEST_DB"'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$POSTGRES_TEST_DB')\gexec
        GRANT ALL PRIVILEGES ON DATABASE "$POSTGRES_TEST_DB" TO "$POSTGRES_USER";
EOSQL
fi
