#!/bin/bash

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
gunicorn education_system.wsgi -w 4 -b 0.0.0.0:8000