#!/bin/bash
set -e

python manage.py collectstatic --noinput &&
daphne -b 0.0.0.0 -p ${PORT:-8000} weatherapp.asgi:application