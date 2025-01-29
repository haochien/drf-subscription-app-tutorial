#!/bin/sh

# Validate environment variables
if [ -z "$DATABASE_HOST" ] || [ -z "$DATABASE_PORT" ]; then
    echo "Error: Database environment variables not set"
    exit 1
fi

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
max_retries=30
retry_count=0
while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
    retry_count=$((retry_count+1))
    if [ $retry_count -gt $max_retries ]; then
        echo "Error: PostgreSQL not available after ${max_retries} retries"
        exit 1
    fi
    sleep 0.1
done
echo "PostgreSQL started"

# Collect static files
echo "Collecting static files..."
if ! python manage.py collectstatic --noinput; then
    echo "Error: Static file collection failed"
    exit 1
fi

# Run migrations
echo "Running migrations..."
if ! python manage.py migrate; then
    echo "Error: Database migration failed"
    exit 1
fi

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn backend.wsgi:application -c gunicorn.conf.py