#!/bin/bash

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
gunicorn base.wsgi:application -c /home/app/gunicorn.conf.py