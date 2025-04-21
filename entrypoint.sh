#!/bin/sh

echo "--< Waiting for PostgreSQL to start..."

while ! pg_isready -h db -p 5432 -U "$POSTGRES_USER"; do
  sleep 1
done

echo "--< PostgreSQL is ready. Running alembic revision..."
poetry run alembic revision --autogenerate -m "Init"
echo "--< PostgreSQL is ready. Running alembic upgrade head..."
poetry run alembic upgrade head

echo "--< Starting the application..."
exec poetry run python main.py