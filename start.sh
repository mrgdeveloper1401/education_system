#!/bin/sh

python manage.py collectstatic --noinput
gunicorn education_system.wsgi -b 0.0.0.0:8000