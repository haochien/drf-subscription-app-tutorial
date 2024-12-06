#!/bin/sh

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
    sleep 0.1
done
echo "PostgreSQL started"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start Gunicorn
exec gunicorn backend.wsgi:application -c gunicorn.conf.py