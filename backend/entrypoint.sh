#!/bin/sh
set -e

echo "Starting Django Entrypoint..."

echo "Waiting for database at db:5432..."
while ! nc -z db 5432; do
  sleep 0.5
done
echo "Database is ready!"

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Starting development server..."
exec python manage.py runserver 0.0.0.0:8000
