#!/bin/bash
set -e

# This script is run by the postgres container on startup.
# It creates the test database if it doesn't already exist.

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE lab_db_test'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'lab_db_test')\gexec
EOSQL