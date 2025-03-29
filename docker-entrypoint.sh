#!/bin/sh

echo "Waiting for database..."
sleep 5  # صبر برای آماده شدن دیتابیس

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Starting Gunicorn..."
exec "$@"  # اجرای دستور اصلی در Dockerfile (مثلاً Gunicorn)
