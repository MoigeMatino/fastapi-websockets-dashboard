#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"
# Run SQL script to set up db
psql -h db -U postgres -d inventory_db -f /setup_db.sql


exec "$@"
