#!/bin/bash
set -e

python manage.py collectstatic --noinput &&
exec gunicorn weatherapp.wsgi:application --bind 0.0.0.0:${PORT:-8000}